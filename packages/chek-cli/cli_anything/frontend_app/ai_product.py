"""AI product publication helpers for CHEK CLI."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .core import HarnessError


AI_PRODUCT_CATEGORIES = ("智能汽车", "具身机器人", "生产力工具", "AI 健康应用", "其他消费级 AI 产品", "AI 健康", "其他")
AI_PRODUCT_CANONICAL_CATEGORIES = ("智能汽车", "具身机器人", "生产力工具", "AI 健康应用", "其他消费级 AI 产品")
AI_PRODUCT_INTEREST_RELATIONS = ("普通用户", "厂商", "代理", "投资人", "媒体", "专家")
AI_PRODUCT_POST_TYPE = "ai_product_review"
AI_PRODUCT_TARGET_TYPE = "ai_product"
ENTITY_REQUIRED_CATEGORIES = {"智能汽车", "具身机器人"}


def clean_text(value: Any) -> str:
    return str(value or "").strip()


def split_list_values(values: tuple[str, ...] | list[str] | None) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for raw in values or []:
        for part in str(raw or "").replace("，", ",").split(","):
            text = part.strip().lstrip("#")
            key = text.lower()
            if not text or key in seen:
                continue
            seen.add(key)
            result.append(text)
    return result


def read_json_file(path: Path | None) -> dict[str, Any]:
    if not path:
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HarnessError("AI product JSON file must be valid JSON.", details={"file": str(path)}) from exc
    if not isinstance(payload, dict):
        raise HarnessError("AI product JSON file must contain a JSON object.", details={"file": str(path)})
    return payload


def pick(*values: Any) -> str:
    for value in values:
        text = clean_text(value)
        if text:
            return text
    return ""


def normalize_category(value: Any) -> str:
    text = pick(value, "其他")
    aliases = {
        "car": "智能汽车",
        "vehicle": "智能汽车",
        "auto": "智能汽车",
        "robot": "具身机器人",
        "humanoid": "具身机器人",
        "productivity": "生产力工具",
        "tool": "生产力工具",
        "health": "AI 健康应用",
        "ai health": "AI 健康应用",
        "AI 健康": "AI 健康应用",
        "ai 健康": "AI 健康应用",
        "其他": "其他消费级 AI 产品",
        "other": "其他消费级 AI 产品",
    }
    text = aliases.get(text.lower(), text)
    return text if text in AI_PRODUCT_CANONICAL_CATEGORIES else "其他消费级 AI 产品"


def normalize_interest_relation(value: Any) -> str:
    text = pick(value, "普通用户")
    return text if text in AI_PRODUCT_INTEREST_RELATIONS else text[:80]


def slug_part(value: Any, fallback: str) -> str:
    text = clean_text(value).lower()
    if not text:
        return fallback
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff._-]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-._")
    return text[:48] or fallback


def product_from_inputs(
    *,
    category: str | None = None,
    product_name: str | None = None,
    hardware_model: str | None = None,
    software_version: str | None = None,
    tags: tuple[str, ...] | list[str] | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = payload or {}
    product = payload.get("product")
    if not isinstance(product, dict):
        product = payload.get("aiProduct") or payload.get("ai_product") or {}
    if not isinstance(product, dict):
        product = {}
    product = {**payload, **product}
    normalized = {
        "category": normalize_category(pick(category, product.get("category"), product.get("product_category"), product.get("productCategory"))),
        "product_name": pick(product_name, product.get("product_name"), product.get("productName"), product.get("name")),
        "hardware_model": pick(hardware_model, product.get("hardware_model"), product.get("hardwareModel"), product.get("hardware")),
        "software_version": pick(software_version, product.get("software_version"), product.get("softwareVersion"), product.get("software")),
        "tags": split_list_values([*split_list_values(tuple(tags or ())), *split_list_values(product.get("tags") or [])]),
    }
    if not normalized["product_name"]:
        raise HarnessError("AI product product_name is required.", details={"field": "product_name"})
    if not normalized["software_version"]:
        raise HarnessError("AI product software_version is required.", details={"field": "software_version"})
    return normalized


def product_title(product: dict[str, Any]) -> str:
    name = clean_text(product.get("product_name"))
    hardware = clean_text(product.get("hardware_model"))
    software = clean_text(product.get("software_version"))
    model_line = " ".join(part for part in (name, hardware) if part)
    return "，".join(part for part in (model_line or name, software) if part) or "AI 产品评审"


def product_identity_label(product: dict[str, Any]) -> str:
    name = clean_text(product.get("product_name"))
    hardware = clean_text(product.get("hardware_model"))
    return " ".join(part for part in (name, hardware) if part) or name or "这款 AI 产品"


def product_target_id(product: dict[str, Any]) -> str:
    return ":".join(
        [
            "ai_product",
            slug_part(product.get("category"), "other"),
            slug_part(product.get("product_name"), "unknown"),
            slug_part(product.get("hardware_model"), "software_only"),
            slug_part(product.get("software_version"), "unknown_version"),
        ]
    )


def duplicate_check_payload(product: dict[str, Any], *, exclude_post_id: str | None = None) -> dict[str, Any]:
    payload = {
        "category": product["category"],
        "product_name": product["product_name"],
        "hardware_model": product.get("hardware_model") or "",
        "software_version": product["software_version"],
        "tags": product.get("tags") or [],
    }
    if clean_text(exclude_post_id):
        payload["exclude_post_id"] = clean_text(exclude_post_id)
    return payload


def source_records(source_urls: tuple[str, ...] | list[str] | None, source_titles: tuple[str, ...] | list[str] | None) -> list[dict[str, str]]:
    urls = [clean_text(url) for url in source_urls or [] if clean_text(url)]
    titles = [clean_text(title) for title in source_titles or [] if clean_text(title)]
    return [
        {"url": url, "title": titles[index] if index < len(titles) else ""}
        for index, url in enumerate(urls)
    ]


def parse_linked_entity(raw: str) -> dict[str, str]:
    text = clean_text(raw)
    if not text:
        return {}
    if text.startswith("{"):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise HarnessError("Linked entity JSON must be valid.", details={"value": text}) from exc
        if not isinstance(parsed, dict):
            raise HarnessError("Linked entity JSON must contain an object.", details={"value": text})
        return {str(key): clean_text(value) for key, value in parsed.items() if clean_text(value)}
    result: dict[str, str] = {}
    for part in re.split(r"[,;，；]", text):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        key = key.strip()
        if key:
            result[key] = value.strip()
    return result


def linked_entities_from_inputs(raw_values: tuple[str, ...] | list[str] | None, payload: dict[str, Any] | None) -> list[dict[str, str]]:
    payload = payload or {}
    existing_extras = payload.get("extras") if isinstance(payload.get("extras"), dict) else {}
    raw_entities: list[Any] = []
    for candidate in (payload.get("linkedEntities"), existing_extras.get("linkedEntities")):
        if isinstance(candidate, list):
            raw_entities.extend(candidate)
    raw_entities.extend(raw_values or [])
    entities: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in raw_entities:
        if isinstance(item, dict):
            entity = {str(key): clean_text(value) for key, value in item.items() if clean_text(value)}
        else:
            entity = parse_linked_entity(str(item))
        target_type = pick(entity.get("targetType"), entity.get("target_type"))
        target_id = pick(entity.get("targetId"), entity.get("target_id"))
        if not target_type or not target_id:
            continue
        normalized = {
            "targetType": target_type,
            "targetId": target_id,
            "title": pick(entity.get("title"), entity.get("name"), entity.get("tagTitle"), target_id),
            "tagTitle": pick(entity.get("tagTitle"), entity.get("title"), entity.get("name"), target_id),
        }
        subtitle = clean_text(entity.get("subtitle"))
        if subtitle:
            normalized["subtitle"] = subtitle
        key = (normalized["targetType"], normalized["targetId"])
        if key in seen:
            continue
        seen.add(key)
        entities.append(normalized)
    return entities


def evidence_text_with_urls(evidence: str | None, evidence_urls: tuple[str, ...] | list[str] | None) -> str:
    lines = [clean_text(evidence)]
    urls = [clean_text(url) for url in evidence_urls or [] if clean_text(url)]
    if urls:
        lines.append("证据链接：" + " ".join(urls))
    return "\n".join(line for line in lines if line)


def summary_from_fields(reason: str, scenario: str, evidence: str) -> str:
    parts = []
    if reason:
        parts.append(f"提报理由：{reason}")
    if scenario:
        parts.append(f"使用场景：{scenario}")
    if evidence:
        parts.append(f"证据：{evidence}")
    return "；".join(parts)[:300]


def summary_from_product(product: dict[str, Any], reason: str, scenario: str) -> str:
    identity = product_identity_label(product)
    software = clean_text(product.get("software_version"))
    base = f"评审 {identity} 在 {software} 下的真实体验。"
    reason_text = clipped_sentence(reason, 110) if reason else ""
    if reason_text:
        return f"{base}{reason_text}"[:220]
    points = review_points(scenario, limit=2)
    if points:
        return f"{base}重点看：{'；'.join(points)}"[:220]
    return base


def clipped_sentence(value: str, limit: int = 120) -> str:
    text = re.sub(r"\s+", " ", clean_text(value))
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip("，,；;。 ") + "..."


def review_points(value: str, *, limit: int = 4) -> list[str]:
    parts = [
        re.sub(r"^[\-*•\d.、\s]+", "", part.strip())
        for part in re.split(r"[\n；;。]+", clean_text(value))
        if part.strip()
    ]
    result: list[str] = []
    seen: set[str] = set()
    for part in parts:
        text = clipped_sentence(part, 48)
        key = text.lower()
        if not text or key in seen:
            continue
        seen.add(key)
        result.append(text)
        if len(result) >= limit:
            break
    return result


def opening_message_from_product(product: dict[str, Any], reason: str, scenario: str) -> str:
    identity = product_identity_label(product)
    software = clean_text(product.get("software_version"))
    reason_text = clipped_sentence(reason, 96) if reason else "请大家用真实体验和可靠证据判断它是否值得进入公开评分。"
    points = review_points(scenario, limit=3)
    lines = [
        f"我们正在评审 {identity} 这个具体版本。",
        f"软件/系统版本：{software}",
        "",
        "这不是泛评品牌，而是看这一版在真实场景里是否好用、稳定、值得推荐。",
        "",
        f"为什么值得测：{reason_text}",
    ]
    if points:
        lines.extend(["", "建议先看："])
        lines.extend(f"- {point}" for point in points)
    lines.extend(["", "用过这一版、跑过资料或能补充可靠证据的朋友，都可以进来打星和补体验。"])
    return "\n".join(lines)


def reader_brief_from_product(
    product: dict[str, Any],
    *,
    reason: str,
    scenario: str,
    interest_relation: str,
    research_sources: list[dict[str, str]],
    cover_source_url: str = "",
) -> str:
    points = review_points(scenario, limit=5)
    identity = product_identity_label(product)
    lines = [
        "评审对象",
        f"- 类别：{product.get('category')}",
        f"- 产品：{clean_text(product.get('product_name'))}",
    ]
    hardware = clean_text(product.get("hardware_model"))
    if hardware:
        lines.append(f"- 硬件型号：{hardware}")
    lines.append(f"- 软件/系统版本：{clean_text(product.get('software_version'))}")
    lines.extend(["", "为什么值得测", clipped_sentence(reason, 180) if reason else f"请围绕 {identity} 的这一具体版本补充实测体验和可靠证据。"])
    if points:
        lines.extend(["", "建议重点看"])
        lines.extend(f"- {point}" for point in points)
    lines.extend(
        [
            "",
            "评分前请确认",
            "- 你评价的是上面的硬件型号和软件版本",
            "- 证据优先使用实测截图、视频、日志、官方文档或可复现仓库",
            f"- 利益关系：{interest_relation}",
        ]
    )
    if research_sources:
        lines.extend(["", "资料入口"])
        for source in research_sources[:3]:
            title = clean_text(source.get("title")) or "来源"
            url = clean_text(source.get("url"))
            lines.append(f"- {title}: {url}" if url else f"- {title}")
    if cover_source_url:
        lines.extend(["", f"封面来源：{cover_source_url}"])
    return "\n".join(lines)


def validate_formal_submission(
    *,
    product: dict[str, Any],
    research_sources: list[dict[str, str]],
    linked_entities: list[dict[str, str]],
    cover_image_url: str,
    cover_source_url: str,
) -> list[str]:
    errors: list[str] = []
    category = normalize_category(product.get("category"))
    if category in ENTITY_REQUIRED_CATEGORIES and not clean_text(product.get("hardware_model")):
        errors.append("智能汽车和具身机器人正式提报必须填写硬件型号。")
    if category in ENTITY_REQUIRED_CATEGORIES and not linked_entities:
        errors.append("智能汽车和具身机器人正式提报必须绑定车型库或机器人库实体。")
    if not research_sources:
        errors.append("正式提报必须提供至少一个联网搜索后的来源 URL。")
    if not clean_text(cover_image_url):
        errors.append("正式提报必须上传封面并传入 CHEK 媒体 URL。")
    if not clean_text(cover_source_url):
        errors.append("正式提报必须记录封面的联网来源 URL。")
    return errors


def robot_config_version_edit_payload(
    *,
    product: dict[str, Any],
    source_repo: str = "",
    source_commit: str = "",
    buddy_post_id: str = "",
    checked_at: str = "",
    title: str = "",
    description: str = "",
) -> dict[str, Any]:
    identity = product_title(product)
    version_name = f"{product_identity_label(product)} / {clean_text(product.get('software_version'))}"
    body = {
        "versionName": version_name,
        "versionType": "community_review",
        "releaseDateText": checked_at or "待确认",
        "isLatest": False,
        "baseInfo": f"CHEK AI 产品评审版本：{identity}。",
        "configSummary": f"硬件型号 {clean_text(product.get('hardware_model')) or '未填写'}；软件/系统版本 {clean_text(product.get('software_version'))}。用于社区评审、复评和榜单追溯。",
        "rawSnapshot": {
            "source": "CHEK CLI AI product review submission",
            "sourceRepo": clean_text(source_repo),
            "sourceCommit": clean_text(source_commit),
            "buddyPostId": clean_text(buddy_post_id),
            "checkedAt": clean_text(checked_at),
        },
    }
    return {
        "title": title or f"新增评审配置版本：{version_name}",
        "description": description or "AI 产品评审房间已绑定真实硬件/软件版本；同步提交机器人资料库配置版本，便于复评和榜单追溯。",
        "diffPayload": {"ops": [{"type": "create_config_version", "body": body}]},
    }


def vehicle_sync_versions_edit_payload(
    *,
    product: dict[str, Any],
    title: str = "",
    description: str = "",
) -> dict[str, Any]:
    hardware = clean_text(product.get("hardware_model"))
    software = clean_text(product.get("software_version"))
    return {
        "title": title or f"新增评审软硬件版本：{product_title(product)}",
        "description": description or "AI 产品评审房间已绑定真实车型硬件/软件版本；同步提交车型资料库版本，便于复评和榜单追溯。",
        "diffPayload": {
            "ops": [
                {
                    "type": "sync_versions",
                    "body": {
                        "hardwareOptions": [hardware] if hardware else [],
                        "softwareOptions": [software] if software else [],
                        "allowDelete": False,
                    },
                }
            ]
        },
    }


def build_publish_payload(
    *,
    product: dict[str, Any],
    reason: str = "",
    scenario: str = "",
    evidence: str = "",
    evidence_urls: tuple[str, ...] | list[str] | None = None,
    interest_relation: str = "普通用户",
    source_urls: tuple[str, ...] | list[str] | None = None,
    source_titles: tuple[str, ...] | list[str] | None = None,
    cover_image_url: str = "",
    media_type: str = "image",
    media_url: str = "",
    cover_source_url: str = "",
    linked_entities: tuple[str, ...] | list[str] | None = None,
    target_id: str = "",
    opening_message: str = "",
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = payload or {}
    existing_extras = payload.get("extras") if isinstance(payload.get("extras"), dict) else {}
    ai_review = existing_extras.get("ai_product_review") if isinstance(existing_extras.get("ai_product_review"), dict) else {}
    reason = pick(reason, ai_review.get("reason"))
    scenario = pick(scenario, ai_review.get("scenario"))
    evidence_text = evidence_text_with_urls(pick(evidence, ai_review.get("evidence")), evidence_urls)
    relation = normalize_interest_relation(pick(interest_relation, ai_review.get("interest_relation"), ai_review.get("interestRelation")))
    research_sources = source_records(source_urls, source_titles)
    if not research_sources and isinstance(ai_review.get("research_sources"), list):
        research_sources = [item for item in ai_review["research_sources"] if isinstance(item, dict)]
    resolved_cover_source_url = pick(cover_source_url, ai_review.get("cover_source_url"), ai_review.get("coverSourceUrl"))
    resolved_linked_entities = linked_entities_from_inputs(linked_entities, payload)
    review_root = {
        **ai_review,
        "reason": reason,
        "scenario": scenario,
        "evidence": evidence_text,
        "interest_relation": relation,
        "interestRelation": relation,
        "research_sources": research_sources,
        "cover_source_url": resolved_cover_source_url,
        "coverSourceUrl": resolved_cover_source_url,
        "agent_assisted": True,
    }
    title = product_title(product)
    reader_brief = reader_brief_from_product(
        product,
        reason=reason,
        scenario=scenario,
        interest_relation=relation,
        research_sources=research_sources,
        cover_source_url=resolved_cover_source_url,
    )
    return {
        "post_type": AI_PRODUCT_POST_TYPE,
        "postType": AI_PRODUCT_POST_TYPE,
        "target_type": AI_PRODUCT_TARGET_TYPE,
        "targetType": AI_PRODUCT_TARGET_TYPE,
        "target_id": pick(target_id, payload.get("target_id"), payload.get("targetId"), product_target_id(product)),
        "targetId": pick(target_id, payload.get("target_id"), payload.get("targetId"), product_target_id(product)),
        "intent_type": AI_PRODUCT_POST_TYPE,
        "intentType": AI_PRODUCT_POST_TYPE,
        "title": pick(payload.get("title"), title),
        "summary": pick(payload.get("summary"), summary_from_product(product, reason, scenario)),
        "cover_image_url": pick(cover_image_url, payload.get("cover_image_url"), payload.get("coverImageUrl")),
        "coverImageUrl": pick(cover_image_url, payload.get("cover_image_url"), payload.get("coverImageUrl")),
        "media_type": pick(media_type, payload.get("media_type"), payload.get("mediaType"), "image"),
        "mediaType": pick(media_type, payload.get("media_type"), payload.get("mediaType"), "image"),
        "media_url": pick(media_url, payload.get("media_url"), payload.get("mediaUrl")),
        "mediaUrl": pick(media_url, payload.get("media_url"), payload.get("mediaUrl")),
        "tags": product.get("tags") or [],
        "product": product,
        "extras": {
            **existing_extras,
            "post_type": AI_PRODUCT_POST_TYPE,
            "postType": AI_PRODUCT_POST_TYPE,
            "product": product,
            "ai_product_review": review_root,
            "linkedEntities": resolved_linked_entities,
            "readerBrief": reader_brief,
            "formalSubmissionRules": [
                "标题只保留产品名、硬件型号和软件版本。",
                "首条消息面向用户阅读，不堆搜索过程和原始材料。",
                "智能汽车和具身机器人必须绑定资料库实体，并同步提交软硬件版本编辑。",
                "封面必须来自联网确认后的产品图，并上传到 CHEK 媒体库。",
            ],
        },
        "opening_message": pick(opening_message, payload.get("opening_message"), payload.get("openingMessage"), opening_message_from_product(product, reason, scenario)),
        "openingMessage": pick(opening_message, payload.get("opening_message"), payload.get("openingMessage"), opening_message_from_product(product, reason, scenario)),
    }


def build_review_payload(
    *,
    rating: float | None = None,
    stars: float | None = None,
    comment: str = "",
    evidence_text: str = "",
    evidence_urls: tuple[str, ...] | list[str] | None = None,
    interest_relation: str = "普通用户",
    tested_version_confirmed: bool = True,
) -> dict[str, Any]:
    resolved = float(rating if rating is not None else (stars or 0) * 2)
    if resolved < 1 or resolved > 10:
        raise HarnessError("Rating must be between 1 and 10, or stars must be between 0.5 and 5.")
    return {
        "rating": round(resolved, 1),
        "comment": clean_text(comment),
        "evidence_text": clean_text(evidence_text),
        "evidence_urls": [clean_text(url) for url in evidence_urls or [] if clean_text(url)],
        "interest_relation": normalize_interest_relation(interest_relation),
        "tested_version_confirmed": bool(tested_version_confirmed),
    }


def build_research_plan(product: dict[str, Any]) -> dict[str, Any]:
    title = product_title(product)
    base = " ".join(
        part
        for part in (
            product.get("product_name"),
            product.get("hardware_model"),
            product.get("software_version"),
        )
        if clean_text(part)
    )
    tags = product.get("tags") or []
    queries = [
        f"{base} 评测 体验",
        f"{base} 发布 更新 日志",
        f"{base} benchmark 跑分",
        f"{base} 问题 缺陷 用户反馈",
        f"{product.get('product_name')} {product.get('software_version')} 官方 文档",
    ]
    if tags:
        queries.append(f"{base} {' '.join(tags[:4])}")
    return {
        "productTitle": title,
        "searchQueries": queries,
        "coverSearchQueries": [
            f"{base} 官方 产品图 封面",
            f"{base} 官方 发布 图片",
            f"{base} product image official",
        ],
        "recommendedSources": [
            "官方发布/更新日志",
            "可信媒体或社区评测",
            "截图、视频、体验记录或跑分链接",
            "同版本硬件型号 + 软件版本的用户反馈",
        ],
        "formalSubmissionChecklist": [
            "联网确认产品名、硬件型号、软件版本和封面来源。",
            "上传封面到 CHEK 媒体库，并保留 cover_source_url。",
            "发布前查重；命中同一版本时进入已有房间。",
            "智能汽车/具身机器人必须绑定车型库或机器人库实体。",
            "智能汽车/具身机器人必须同步提交资料库软硬件版本编辑。",
            "房间首条消息必须是用户可读邀请，不发布原始搜索日志。",
        ],
        "duplicateCheck": duplicate_check_payload(product),
        "publishRule": "发布前应先查重；命中重复时进入已有房间评测，除非明确使用 duplicate-policy=allow。",
        "reviewRule": "评分证据应说明测试场景、版本确认、利益关系；公开评分门槛只看追日靴有效评分数。",
    }
