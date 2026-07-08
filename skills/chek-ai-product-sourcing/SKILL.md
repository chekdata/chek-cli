---
name: chek-ai-product-sourcing
description: Source, verify, classify, and package CHEK AI product candidates for either local output or a user-specified Feishu/Lark candidate base, including optional Zhihu Developer on-site search evidence. Use when the user asks to search for AI products, fill or update a CHEK candidate pool, apply monthly or quarterly release windows, assess domestic availability/borrowability, prepare fields for AI product submission, check duplicate product candidates, use developer.zhihu.com/Zhihu site search, or decide which candidates should be submitted later through the CHEK CLI.
---

# CHEK AI Product Sourcing

## Overview

Use this skill to maintain the CHEK AI product candidate pool before formal submission. The normal output is an evidence-backed candidate dataset written either to local files or to a user-specified Feishu Base, not immediate CLI submission.

Read [references/candidate-base.md](references/candidate-base.md) before writing records, changing status labels, summarizing counts, or deciding whether a product is eligible.

Read [references/zhihu-developer-search.md](references/zhihu-developer-search.md) before using `developer.zhihu.com`, the Zhihu search API, or Zhihu on-site search results as evidence.

## Operating Rules

- Browse the web for current product facts, release dates, versions, prices, official pages, App Store listings, and availability. Prefer official product pages, App Store pages, manufacturer pages, store pages, and reputable media.
- Treat product and release information as time-sensitive. Do not rely on memory for "latest", "recent", "this month", or version claims.
- Use Zhihu Developer on-site search as an additional Chinese discussion and experience-report source when credentials are available. Do not use Zhihu as the only source for release date, version, availability, or official capability claims.
- Do not assume a default Feishu Base. If the user has not chosen an output target, ask whether to output local files or write to a user-specified Feishu/Lark Base.
- Use `lark-base` before operating Feishu Base. Follow its rule to read field structure before writing and to avoid concurrent `+record-list` calls.
- Do not submit products through the CHEK CLI unless the user explicitly confirms which candidates to submit.
- Keep the Base simple. Do not add columns unless the user explicitly asks.
- Deduplicate before writing. Check existing product names and, for final submission, also check product name + hardware model + software version.
- Be honest about domestic access. Do not say a product can be borrowed or tested unless a source supports that. Use `待渠道确认` or `待实测材料` when access is plausible but unproven.
- For pure software products, hardware model may be empty, but software version must be specific. For hardware, cars, robots, and glasses, capture both hardware model and software/firmware/app/vehicle version whenever possible.

## Workflow

1. Confirm the active statistical window.
   - If the user gives a window, use it exactly.
   - If the user says to use a larger window for this project, use `2026-03-15~2026-06-15` as the quarterly window unless they override it.
   - Keep monthly windows as tags or filters, not as the only search boundary, when the user asks for quarterly sourcing.

2. Build search coverage by category.
   - Search by product category, brand, ecosystem, capability, hardware form factor, model supplier, and release wording.
   - Avoid relying only on "AI", "large model", "Agent", or head-brand keywords; this caused missed candidates such as `上汽大众 ID. ERA 9X`.
   - If a Zhihu Developer Access Secret is available, run focused Zhihu site-search queries for user reports, evaluations, issues, comparisons, and domestic availability clues. Keep official sources as the final authority for factual fields.

3. Verify candidate eligibility.
   - Confirm it is public-facing and consumer-usable: purchasable, downloadable, registerable, testable, or at least clearly available through a domestic trial/channel.
   - Confirm the event is within the active window: release, preorder, launch, OTA, app version update, public beta, model upgrade, or official availability.
   - Confirm the product has AI-relevant review value, not just generic digital functionality.

4. Classify status.
   - Use the status guidance in [references/candidate-base.md](references/candidate-base.md).
   - Prefer actionable status labels such as `建议提报`, `待实测材料`, `待渠道确认`, `待证据确认`, and `观察暂缓`.

5. Choose and write the output target.
   - If the target is local, write a Markdown, CSV, or JSON artifact in the current workspace, based on the user's requested format.
   - If the target is Feishu/Lark, use only the Base/Wiki/table identifiers supplied by the user for this run.
   - Read the Feishu table schema first, then read existing records and dedupe.
   - Use `lark-cli base +record-upsert` with direct field-name JSON.
   - Write compact, evidence-backed fields. Include source URLs in `证据来源`.

6. Promote the next-step shortlist when requested.
   - Do not add new Base columns for routine prioritization.
   - Use existing fields: set `重点` to `是`, write `P0` or `P1` at the start of `待补材料`, and explain the priority in `月度依据`.
   - Use `P0` for immediate formal-review or same-week evidence collection candidates, and `P1` for comparison samples,复评跟随项, or useful but non-window references.
   - For复评 events, preserve the original candidate and add a dated复评任务包 instead of overwriting the earlier version logic.

7. Summarize after changes.
   - Report inserted or updated products, or the local file path written.
   - For Feishu output, report total record count and duplicate check result.
   - For Feishu output, use `+data-query` for counts by `状态`, `类别`, and `统计时间窗口口径`.
   - State explicitly that CLI product submission has not been performed unless it actually has.

## Search Coverage Checklist

Use this checklist when the user asks whether anything is missing:

- 智能汽车: search vehicle brands plus suppliers and capability names such as Momenta, 文远知行, 地平线, 大卓, ADiGO, 乾崑, ADS, 端到端, 世界模型, 城市NOA, OTA, 增程, 合资品牌.
- 具身机器人: search 人形机器人, 家庭服务机器人, 管家机器人, 陪伴机器人, 仿生宠物, 扫地/割草机器人, 家电品牌, AWE, 官方商城, 招募, 试用.
- 生产力工具: search independent apps plus platform-embedded entrances: browsers, search, office suites, knowledge bases, plugins, app stores, mobile versions, web versions.
- AI 健康应用: search independent apps plus platform entrances and mini-programs: 百度健康, 支付宝健康, 微信生态, AI+真人, 家庭医生, 报告解读, 症状自查, 免责声明.
- 其他消费级 AI 产品: search AI glasses, AI recorder cards, AI recorder pens, wearable assistants, cameras, creator tools, video/image apps, phone-vendor ecosystem hardware.

## Final Submission Boundary

Candidate sourcing and formal product submission are separate phases.

Before formal CLI submission, re-check duplicate rooms online, lock the exact version tuple, and confirm with the user. Formal submission should fill richer fields from the candidate record and current web search, then route users to any existing room when a duplicate is found.
