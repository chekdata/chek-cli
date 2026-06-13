"""AI product publication helpers for CHEK CLI."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .core import HarnessError


AI_PRODUCT_CATEGORIES = ("智能汽车", "具身机器人", "生产力工具", "AI 健康", "其他")
AI_PRODUCT_INTEREST_RELATIONS = ("普通用户", "厂商", "代理", "投资人", "媒体", "专家")
AI_PRODUCT_POST_TYPE = "ai_product_review"
AI_PRODUCT_TARGET_TYPE = "ai_product"


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
        "health": "AI 健康",
        "ai health": "AI 健康",
        "other": "其他",
    }
    text = aliases.get(text.lower(), text)
    return text if text in AI_PRODUCT_CATEGORIES else "其他"


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


def opening_message_from_fields(reason: str, scenario: str, evidence: str, interest_relation: str) -> str:
    lines = []
    if reason:
        lines.append(f"提报理由：{reason}")
    if scenario:
        lines.append(f"使用场景：{scenario}")
    if evidence:
        lines.append(f"证据材料：{evidence}")
    if interest_relation:
        lines.append(f"利益关系：{interest_relation}")
    return "\n".join(lines)[:300]


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
    review_root = {
        **ai_review,
        "reason": reason,
        "scenario": scenario,
        "evidence": evidence_text,
        "interest_relation": relation,
        "interestRelation": relation,
        "research_sources": research_sources,
        "agent_assisted": True,
    }
    title = product_title(product)
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
        "summary": pick(payload.get("summary"), summary_from_fields(reason, scenario, evidence_text)),
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
        },
        "opening_message": pick(opening_message, payload.get("opening_message"), payload.get("openingMessage"), opening_message_from_fields(reason, scenario, evidence_text, relation)),
        "openingMessage": pick(opening_message, payload.get("opening_message"), payload.get("openingMessage"), opening_message_from_fields(reason, scenario, evidence_text, relation)),
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
        "recommendedSources": [
            "官方发布/更新日志",
            "可信媒体或社区评测",
            "截图、视频、体验记录或跑分链接",
            "同版本硬件型号 + 软件版本的用户反馈",
        ],
        "duplicateCheck": duplicate_check_payload(product),
        "publishRule": "发布前应先查重；命中重复时进入已有房间评测，除非明确使用 duplicate-policy=allow。",
        "reviewRule": "评分证据应说明测试场景、版本确认、利益关系；公开评分门槛只看追日靴有效评分数。",
    }
