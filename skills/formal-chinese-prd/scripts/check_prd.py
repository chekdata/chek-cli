#!/usr/bin/env python3
"""Deterministic structural and wording checks for formal Chinese PRDs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath


@dataclass(frozen=True)
class Finding:
    level: str
    code: str
    line: int
    message: str
    snippet: str = ""


def add(
    findings: list[Finding],
    level: str,
    code: str,
    line: int,
    message: str,
    snippet: str = "",
) -> None:
    findings.append(
        Finding(level, code, line, message, snippet.strip()[:180])
    )


def visible_lines(lines: list[str]) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    in_fence = False
    fence = ""
    in_comment = False

    for line_number, raw in enumerate(lines, 1):
        stripped = raw.strip()
        fence_match = re.match(r"^(```+|~~~+)", stripped)
        if fence_match:
            marker = fence_match.group(1)[0]
            if not in_fence:
                in_fence = True
                fence = marker
            elif marker == fence:
                in_fence = False
                fence = ""
            continue
        if in_fence:
            continue

        line = raw
        if in_comment:
            if "-->" in line:
                line = line.split("-->", 1)[1]
                in_comment = False
            else:
                continue
        while "<!--" in line:
            before, after = line.split("<!--", 1)
            if "-->" in after:
                after = after.split("-->", 1)[1]
                line = before + after
            else:
                line = before
                in_comment = True
                break
        result.append((line_number, line))
    return result


def parse_cells(line: str) -> list[str] | None:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return None
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def is_separator_row(cells: list[str] | None) -> bool:
    if not cells:
        return False
    return all(bool(re.fullmatch(r":?-{3,}:?", cell.replace(" ", ""))) for cell in cells)


def plain_text(value: str) -> str:
    value = re.sub(r"[`*_~]", "", value)
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", "", value)


def check_headings(
    visible: list[tuple[int, str]], findings: list[Finding]
) -> None:
    nonempty = [(n, line) for n, line in visible if line.strip()]
    h1 = [(n, line) for n, line in visible if re.match(r"^#(?!#)\s+\S", line)]
    if len(h1) != 1:
        add(findings, "ERROR", "HEAD001", 1, f"文档必须且只能有一个 H1，当前为 {len(h1)} 个")
    if nonempty and not re.match(r"^#(?!#)\s+\S", nonempty[0][1]):
        add(
            findings,
            "ERROR",
            "HEAD002",
            nonempty[0][0],
            "第一条非空内容必须是未编号的 H1 文档标题",
            nonempty[0][1],
        )

    expected_h2 = 1
    current_h2: int | None = None
    expected_h3 = 1
    for line_number, line in visible:
        if re.match(r"^#{4,}\s+", line):
            add(
                findings,
                "WARN",
                "HEAD003",
                line_number,
                "默认结构不建议使用 H4 或更深标题，请确认层级确有必要",
                line,
            )
        if re.match(r"^##(?!#)\s+", line):
            match = re.match(r"^##\s+(\d+)\.\s+(.+)$", line)
            if not match:
                add(
                    findings,
                    "ERROR",
                    "HEAD004",
                    line_number,
                    "H2 必须使用“## N. 标题”格式",
                    line,
                )
                current_h2 = None
                continue
            number = int(match.group(1))
            if number != expected_h2:
                add(
                    findings,
                    "ERROR",
                    "HEAD005",
                    line_number,
                    f"H2 编号应为 {expected_h2}，实际为 {number}",
                    line,
                )
                expected_h2 = number
            current_h2 = number
            expected_h2 += 1
            expected_h3 = 1
        elif re.match(r"^###(?!#)\s+", line):
            match = re.match(r"^###\s+(\d+)\.(\d+)\s+(.+)$", line)
            if not match:
                add(
                    findings,
                    "ERROR",
                    "HEAD006",
                    line_number,
                    "H3 必须使用“### N.M 标题”格式",
                    line,
                )
                continue
            parent, number = int(match.group(1)), int(match.group(2))
            if current_h2 is None or parent != current_h2:
                add(
                    findings,
                    "ERROR",
                    "HEAD007",
                    line_number,
                    "H3 的一级编号必须与当前 H2 一致",
                    line,
                )
            if number != expected_h3:
                add(
                    findings,
                    "ERROR",
                    "HEAD008",
                    line_number,
                    f"当前章节的 H3 编号应为 {expected_h3}，实际为 {number}",
                    line,
                )
                expected_h3 = number
            expected_h3 += 1


def check_style(visible: list[tuple[int, str]], findings: list[Finding]) -> None:
    hard_rules = [
        ("STYLE001", re.compile(r"一句话(?:说明|概述|总结|介绍)"), "删除不正式的“一句话……”标题，直接使用正式主题名称"),
        ("STYLE002", re.compile(r"不是.{0,40}?而是"), "删除“不是……而是……”模板句，直接定义对象或分别说明状态"),
        ("STYLE003", re.compile(r"\b(?:TODO|FIXME|TBD)\b|待补充|待完善|占位内容|\{\{[^{}]+\}\}", re.I), "交付文档不得保留占位内容"),
        ("STYLE004", re.compile(r"作为一个\s*(?:AI|人工智能)|由\s*AI\s*生成", re.I), "产品正文不得暴露生成过程"),
    ]
    warning_rules = [
        ("STYLE101", re.compile(r"不等于|而非"), "避免模板化对比，改为直接说明各对象的定义和条件"),
        ("STYLE102", re.compile(r"下面将|接下来将|本节将|综上所述|总而言之|由此可见|不难发现|显而易见|值得注意的是|需要指出的是"), "删除写作过程和过渡套话"),
        ("STYLE103", re.compile(r"一站式|革命性|颠覆性|行业领先|业界领先|极致体验|无缝衔接|全面赋能|智能化赋能"), "将宣传词改为可观察的产品范围、行为或指标"),
        ("STYLE104", re.compile(r"打通|拉通|抓手|形成闭环|高效闭环|兜底|贯通全链路"), "将项目黑话改为明确动作、责任人和结果"),
        ("STYLE105", re.compile(r"业务化错误|原始事实|原地修改|容量投影|完整链路|鉴权"), "使用符合中文业务语境的正式词汇"),
        ("STYLE106", re.compile(r"我们将|我们可以"), "删除作者视角，直接陈述产品要求"),
    ]
    implementation_rules = [
        ("TECH101", re.compile(r"仓库结构|代码仓库|源码|代码实现|代码提交记录|Git\s*提交|\bcommit\b|\bpull request\b|\bPR\b|\bissue\b", re.I), "产品正文疑似包含仓库或研发过程信息"),
        ("TECH102", re.compile(r"(?:^|[\s`])(?:src|packages)/|package\.json|Cargo\.toml|pyproject\.toml|[\w./-]+\.(?:ts|tsx|js|jsx|py|rs|go|java|cpp|proto)(?:\b|`)", re.I), "产品正文疑似包含工程路径或源文件"),
        ("TECH103", re.compile(r"Electron|Tauri|React|Vue|Node\.js|SQLite|PostgreSQL|Redis|Docker|Kubernetes", re.I), "请确认技术栈名称是否构成对外产品约束；否则移出 PRD"),
        ("TECH104", re.compile(r"数据库表|API\s*(?:路由|端点|地址)|endpoint|消息队列|线程池|类名|函数名|方法名|采用.{0,20}框架|基于.{0,20}实现|调用.{0,20}API|写入.{0,20}表", re.I), "请将实现机制转译为用户可感知的产品行为"),
        ("TECH105", re.compile(r"(?:^|[\s`])/(?:home|Users|workspace|opt|var)/[^\s`]+"), "产品正文不得包含本地绝对路径"),
    ]

    for line_number, line in visible:
        scan = re.sub(r"\]\([^)]*\)", "]", line)
        for code, pattern, message in hard_rules:
            if pattern.search(scan):
                add(findings, "ERROR", code, line_number, message, line)
        for code, pattern, message in warning_rules + implementation_rules:
            if pattern.search(scan):
                add(findings, "WARN", code, line_number, message, line)


def check_requirement_tables(
    visible: list[tuple[int, str]], findings: list[Finding]
) -> None:
    header = ["编号", "优先级", "需求", "验收要点"]
    id_pattern = re.compile(r"^[A-Z][A-Z0-9]{1,8}-\d{2,3}$")
    all_id_pattern = re.compile(r"\b[A-Z][A-Z0-9]{1,8}-\d{2,3}\b")
    vague = re.compile(r"尽可能|适当|合理|尽快|大约|若干|视情况|原则上|友好|高效|快速|稳定运行|显著提升")
    definitions: dict[str, int] = {}
    prefix_numbers: dict[str, list[tuple[int, int]]] = defaultdict(list)

    index = 0
    while index < len(visible):
        line_number, line = visible[index]
        cells = parse_cells(line)
        if cells != header:
            index += 1
            continue
        if index + 1 >= len(visible) or not is_separator_row(parse_cells(visible[index + 1][1])):
            add(findings, "ERROR", "REQ001", line_number, "需求表头后必须紧跟 Markdown 分隔行", line)
            index += 1
            continue

        row_index = index + 2
        while row_index < len(visible):
            row_line_number, row_line = visible[row_index]
            row_cells = parse_cells(row_line)
            if row_cells is None or is_separator_row(row_cells):
                break
            if len(row_cells) != 4:
                add(findings, "ERROR", "REQ002", row_line_number, "需求表每行必须恰好包含四列", row_line)
                row_index += 1
                continue
            requirement_id, priority, requirement, acceptance = row_cells
            if not all(row_cells):
                add(findings, "ERROR", "REQ003", row_line_number, "需求表不得包含空单元格", row_line)
            if not id_pattern.fullmatch(requirement_id):
                add(findings, "ERROR", "REQ004", row_line_number, "需求编号应使用 PREFIX-01 格式", requirement_id)
            else:
                if requirement_id in definitions:
                    add(
                        findings,
                        "ERROR",
                        "REQ005",
                        row_line_number,
                        f"需求编号重复，首次出现在第 {definitions[requirement_id]} 行",
                        requirement_id,
                    )
                else:
                    definitions[requirement_id] = row_line_number
                prefix, number = requirement_id.rsplit("-", 1)
                prefix_numbers[prefix].append((int(number), row_line_number))
            if priority not in {"P0", "P1", "P2"}:
                add(findings, "ERROR", "REQ006", row_line_number, "优先级只能使用 P0、P1 或 P2", priority)
            if vague.search(requirement) or vague.search(acceptance):
                add(findings, "WARN", "REQ101", row_line_number, "需求包含难以验收的模糊词，请补充条件、结果或测量口径", row_line)
            if requirement and acceptance and plain_text(requirement) == plain_text(acceptance):
                add(findings, "WARN", "REQ102", row_line_number, "验收要点不得只复述需求原句", row_line)
            row_index += 1
        index = row_index

    for prefix, numbered in sorted(prefix_numbers.items()):
        numbers = sorted({number for number, _ in numbered})
        expected = list(range(1, max(numbers) + 1)) if numbers else []
        if numbers != expected:
            line_number = min(line for _, line in numbered)
            add(
                findings,
                "ERROR",
                "REQ007",
                line_number,
                f"{prefix} 编号应从 01 连续递增，实际为 {numbers}",
            )

    defined_prefixes = {requirement_id.rsplit("-", 1)[0] for requirement_id in definitions}
    for line_number, line in visible:
        for reference in all_id_pattern.findall(line):
            prefix = reference.rsplit("-", 1)[0]
            if prefix in defined_prefixes and reference not in definitions:
                add(findings, "WARN", "REQ103", line_number, f"正文引用了未定义的需求编号 {reference}", line)


def normalize_caption(value: str) -> str:
    return re.sub(r"\s+", "", value.replace("　", " "))


def check_images(
    document_path: Path,
    visible: list[tuple[int, str]],
    findings: list[Finding],
) -> None:
    image_pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
    caption_pattern = re.compile(r"^<div\s+align=[\"']center[\"']>(.*?)</div>$", re.I)
    figure_pattern = re.compile(r"^图\s*(\d+)[\s　]+(.+)$")
    allowed_extensions = {".png", ".jpg", ".jpeg", ".svg", ".webp"}
    figures: list[tuple[int, int]] = []
    referenced_paths: dict[str, int] = {}

    for position, (line_number, line) in enumerate(visible):
        for match in image_pattern.finditer(line):
            alt, target = match.group(1).strip(), match.group(2).strip()
            if not alt:
                add(findings, "ERROR", "IMG001", line_number, "图片必须包含描述性替代文本", line)

            if re.match(r"^[a-z]+://", target, re.I) or target.startswith("data:"):
                add(findings, "ERROR", "IMG002", line_number, "产品文档图片必须使用 assets/ 下的本地相对路径", target)
                continue
            normalized_target = target.replace("\\", "/")
            pure = PurePosixPath(normalized_target)
            if pure.is_absolute() or ".." in pure.parts or not pure.parts or pure.parts[0] != "assets":
                add(findings, "ERROR", "IMG003", line_number, "图片路径必须位于当前文档的 assets/ 目录内", target)
                continue
            extension = Path(normalized_target).suffix.lower()
            if extension not in allowed_extensions:
                add(findings, "ERROR", "IMG004", line_number, f"不支持的图片格式 {extension}", target)
            asset = (document_path.parent / normalized_target).resolve()
            try:
                asset.relative_to(document_path.parent.resolve())
            except ValueError:
                add(findings, "ERROR", "IMG005", line_number, "图片路径逃逸出文档目录", target)
            if not asset.exists():
                add(findings, "ERROR", "IMG006", line_number, "图片文件不存在", target)
            if normalized_target in referenced_paths:
                add(
                    findings,
                    "WARN",
                    "IMG101",
                    line_number,
                    f"图片已在第 {referenced_paths[normalized_target]} 行引用",
                    target,
                )
            else:
                referenced_paths[normalized_target] = line_number

            figure_match = figure_pattern.fullmatch(alt)
            if not figure_match:
                add(findings, "ERROR", "FIG001", line_number, "图片替代文本必须使用“图 N　标题”格式", alt)
            else:
                figures.append((int(figure_match.group(1)), line_number))

            next_nonempty: tuple[int, str] | None = None
            for candidate in visible[position + 1 :]:
                if candidate[1].strip():
                    next_nonempty = candidate
                    break
            if next_nonempty is None:
                add(findings, "ERROR", "FIG002", line_number, "图片后缺少居中图题", alt)
            else:
                caption_match = caption_pattern.fullmatch(next_nonempty[1].strip())
                if not caption_match:
                    add(findings, "ERROR", "FIG003", next_nonempty[0], "图片后第一条非空内容必须是居中图题", next_nonempty[1])
                elif normalize_caption(caption_match.group(1)) != normalize_caption(alt):
                    add(findings, "ERROR", "FIG004", next_nonempty[0], "图片替代文本与图题不一致", next_nonempty[1])

            if "核心业务流程" in alt:
                if extension != ".png":
                    add(findings, "WARN", "FIG101", line_number, "核心业务流程建议使用 PlantUML 转换的 PNG", target)
                elif not asset.with_suffix(".puml").exists():
                    add(findings, "WARN", "FIG102", line_number, "核心业务流程 PNG 缺少同名 PlantUML 源文件", target)

    numbers = [number for number, _ in figures]
    expected = list(range(1, len(numbers) + 1))
    if numbers != expected:
        line_number = figures[0][1] if figures else 1
        add(findings, "ERROR", "FIG005", line_number, f"图号应从 1 连续递增，实际为 {numbers}")


def main() -> int:
    parser = argparse.ArgumentParser(description="检查正式中文产品需求说明书的结构、用词、需求表和图片")
    parser.add_argument("document", type=Path, help="Markdown PRD 路径")
    parser.add_argument("--strict", action="store_true", help="存在 WARN 时也返回失败")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="输出格式")
    args = parser.parse_args()

    document_path = args.document.expanduser().resolve()
    if not document_path.is_file():
        print(f"ERROR FILE001: 文件不存在：{document_path}", file=sys.stderr)
        return 2

    try:
        text = document_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print("ERROR FILE002: 文档必须使用 UTF-8 编码", file=sys.stderr)
        return 2

    lines = text.splitlines()
    visible = visible_lines(lines)
    findings: list[Finding] = []

    check_headings(visible, findings)
    check_style(visible, findings)
    check_requirement_tables(visible, findings)
    check_images(document_path, visible, findings)

    severity = {"ERROR": 0, "WARN": 1}
    findings.sort(key=lambda item: (item.line, severity[item.level], item.code))
    errors = sum(item.level == "ERROR" for item in findings)
    warnings = sum(item.level == "WARN" for item in findings)

    if args.format == "json":
        print(
            json.dumps(
                {
                    "document": str(document_path),
                    "errors": errors,
                    "warnings": warnings,
                    "findings": [asdict(item) for item in findings],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        for item in findings:
            location = f"第 {item.line} 行" if item.line else "文档"
            print(f"{item.level} {item.code} {location}: {item.message}")
            if item.snippet:
                print(f"  {item.snippet}")
        if not findings:
            print("PASS：未发现结构、链接或禁用表达问题。")
        print(f"检查完成：{errors} 个错误，{warnings} 个警告。")

    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
