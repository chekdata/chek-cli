---
name: chek-ai-product-sourcing
description: Source, verify, classify, and package CHEK AI product candidates for either local output or a user-specified Feishu/Lark candidate base, including optional Zhihu Developer on-site search evidence and user review-material processing. Use when the user asks to search for AI products, fill or update a CHEK candidate pool, apply monthly or quarterly release windows, assess domestic availability/borrowability, prepare fields for AI product submission, check duplicate product candidates, use developer.zhihu.com/Zhihu site search, turn recordings/transcripts/notes into user-friendly AI product reviews, or decide which candidates/reviews should be submitted later through the CHEK CLI.
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
- Do not publish user review material to a CHEK room unless the user explicitly confirms the target room or exact product tuple and authorizes posting.
- Keep the Base simple. Do not add columns unless the user explicitly asks.
- Deduplicate before writing. Check existing product names and, for final submission, also check product name + hardware model + software version.
- Be honest about domestic access. Do not say a product can be borrowed or tested unless a source supports that. Use `待渠道确认` or `待实测材料` when access is plausible but unproven.
- For pure software products, hardware model may be empty, but software version must be specific. For hardware, cars, robots, and glasses, capture both hardware model and software/firmware/app/vehicle version whenever possible.
- For user recordings, transcripts, or rough notes, preserve the user's actual experience while removing private information, license plates, phone numbers, exact addresses, account identifiers, and unrelated personal details.

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

## Review Material To Room Workflow

Use this workflow when the user wants Agent help turning a product test, voice memo, transcript, shorthand notes, screenshots, videos, or links into a CHEK review-room contribution.

1. **Collect material**
   - Ask for the target room URL/post id or the exact `产品名 + 硬件型号 + 软件版本`.
   - Accept audio files, transcripts, rough notes, photos, screenshots, video links, app logs, route/test summaries, and source URLs.
   - If only audio is provided and the environment cannot transcribe it, ask the user for a transcript or concise voice-note export.

2. **Extract review facts**
   - Identify the exact product version, test date, test location or broad setting, scenario, duration, reviewer role, and evidence files.
   - Extract what the user actually observed: successful tasks, failure cases, surprises, constraints, and confidence level.
   - Separate facts from interpretation. Mark unclear claims as `待确认`, not as final conclusions.
   - For intelligent vehicles and robots, keep hardware model and software/firmware/OTA version visible in the review draft.

3. **Write user-friendly review content**
   - Write like a community member sharing a useful test, not like an API report.
   - Start with the tested version and one clear takeaway.
   - Frame the user's contribution as a reusable review archive and public evidence that helps others choose, re-review, or avoid pitfalls.
   - Include scenario, what worked, what failed or felt risky, who this version may suit, and what evidence is attached.
   - Avoid backend field names, source-dump formatting, long search logs, or exaggerated ranking claims.
   - If the user gives enough signal for a rating, suggest a star score and explain the reason; otherwise ask the user to choose the score.

4. **Find the correct room**
   - If a post id is given, read back room detail before posting.
   - If no room is given, run duplicate-room lookup by `产品名 + 硬件型号 + 软件版本`.
   - If a duplicate room exists, post there instead of creating a new room.
   - If no room exists, prepare a candidate submission summary and ask for explicit confirmation before formal CHEK CLI publication.

5. **Post only after confirmation**
   - Before any mutating command, verify prod with:

```bash
chek --json config show
chek auth status
```

   - Use `chek ai-product +review` for star rating, review comment, and evidence when available.
   - For follow-up room messages, discover the generated message command with `chek routes find buddy posts messages` or use the repository-supported room-message helper. Do not invent an endpoint.
   - After posting, read back the room and confirm the review/evidence appears once.

## Review Draft Template

```text
我这次测的是 <产品名> <硬件型号>，软件/系统版本是 <版本>。

一句话结论：<最重要、最像用户真实体验的判断>

测试场景：
- <场景 1>
- <场景 2>

表现不错的地方：
- <观察到的优点>

需要注意的问题：
- <观察到的问题或限制>

我的评分：<星级，如果用户已确认>

证据材料：
- <截图/视频/链接/记录>

补充说明：这次结论只对应上述硬件和软件版本，后续 OTA 或固件变化后建议复评。
```

## Search Coverage Checklist

Use this checklist when the user asks whether anything is missing:

- 智能汽车: search vehicle brands plus suppliers and capability names such as Momenta, 文远知行, 地平线, 大卓, ADiGO, 乾崑, ADS, 端到端, 世界模型, 城市NOA, OTA, 增程, 合资品牌.
- 具身机器人: search 人形机器人, 家庭服务机器人, 管家机器人, 陪伴机器人, 仿生宠物, 扫地/割草机器人, 家电品牌, AWE, 官方商城, 招募, 试用.
- 生产力工具: search independent apps plus platform-embedded entrances: browsers, search, office suites, knowledge bases, plugins, app stores, mobile versions, web versions.
- AI 健康应用: search independent apps plus platform entrances and mini-programs: 百度健康, 支付宝健康, 微信生态, AI+真人, 家庭医生, 报告解读, 症状自查, 免责声明.
- 其他消费级 AI 产品: search AI glasses, AI recorder cards, AI recorder pens, wearable assistants, cameras, creator tools, video/image apps, phone-vendor ecosystem hardware.

## Final Submission Boundary

Candidate sourcing and formal product submission are separate phases.

Formal CHEK CLI submission in this skill is production-only. Before any mutating CHEK command, run:

```bash
chek --json config show
chek auth status
```

Proceed only when the config reports `env=prod` and `api_origin=https://api.chekkk.com`. If either value is different, run `chek config set-env prod`, re-run `chek --json config show`, and continue only after the user has confirmed a formal production submission. Do not publish, edit, review, approve, upload media, or mutate vehicle/robot library data from this skill unless the active CHEK CLI target is production.

Before formal CLI submission, re-check duplicate rooms online, lock the exact version tuple, and confirm with the user. Formal submission should fill richer fields from the candidate record and current web search, then route users to any existing room when a duplicate is found.

Formal CHEK CLI submission workflow:

1. Lock a clean, real version tuple.
   - Required tuple: `产品名 + 硬件型号 + 软件版本`.
   - Pure software products may leave `硬件型号` blank, but `软件版本` must be date-specific or version-specific.
   - Intelligent vehicles and robots must include the real trim/SKU/hardware scope and the exact software/system/firmware/SDK version.
   - Do not set `硬件型号` equal to `产品名`; use a meaningful trim, SKU, scope, or hardware generation so the generated room title does not repeat itself.

2. Keep user-facing text clean.
   - The room title should read like a product review object, not a worklog: product + non-duplicative hardware/trim/scope + software version.
   - Do not put sourcing notes, "资料整理", "榜单支撑", dates, internal IDs, backend field names, or debug labels in the title.
   - The opening room message must answer: what exact version is being reviewed, why it is worth testing, and how users can participate.
   - Do not paste raw search logs, long evidence dumps, or candidate-table field names into the first message.

3. Search and prepare evidence.
   - Re-run current web search immediately before publishing. Prefer official product pages, official announcements, manufacturer media, app stores, GitHub/social preview images, or reputable media.
   - Use Zhihu Developer search only as discussion and clue evidence; keep official pages, app stores, manufacturer announcements, stores, or reputable media as factual authority for release/version/availability.
   - Search for a real cover image online. Prefer official/reputable images that show the actual product or software UI. Upload the selected image to CHEK media when the CLI exposes a media-upload command; otherwise stop and report the upload capability gap instead of publishing without a CHEK media URL.
   - Preserve both the CHEK media URL and the original cover source URL.

4. Resolve canonical tags and library bindings.
   - For vehicles, search the vehicle library first with `chek vehicle +search --query "<产品或车型>"`.
   - For robots, search the robot library first with `chek humanoid +search --query "<产品或型号>"` and inspect versions with `chek humanoid +config --id <robot_id>`.
   - Bind the review room to the canonical entity through the installed CLI's supported linked-entity option or JSON draft field. Verify the published room preserves the full target type and target id; if the returned tag/entity is truncated or missing, stop and report the binding issue.
   - If the matching vehicle or robot main entry does not exist, do not publish an unbound formal review room. Put the candidate into a main-entry-needed queue and ask for the governance/main-entry flow.

5. Synchronize version data for vehicles and robots.
   - Submit the matching vehicle or robot version edit before or alongside the room using the installed CLI's supported command. Prefer formal shortcuts such as `chek ai-product +vehicle-version-edit` or `chek ai-product +robot-version-edit` when they exist; otherwise confirm the generated schema command with `chek schema` or `chek routes find` before any production mutation.
   - For vehicles, verify the new hardware/software pair by reading vehicle detail and software options after the edit is approved or applied.
   - For robots, verify the new config/version by reading robot detail and config versions after the edit is approved or applied.
   - If the write succeeds but readback does not show the expected version, mark the library sync unresolved and do not claim the formal binding is complete.

6. Duplicate-check and publish.
   - Run `chek ai-product +duplicate-check` against `产品名 + 硬件型号 + 软件版本`.
   - If a duplicate exists, do not publish; return the existing room and suggest adding evidence or a review there.
   - Run `chek ai-product +publish` only after duplicate check, cover upload, source collection, and canonical binding are ready. If the installed CLI exposes a `--formal` flag, use it for official review rooms.
   - Keep evidence layered: concise reader-facing explanation in the room, key links only, and raw URLs/commit/source details in structured fields or follow-up evidence messages.

7. Verify after publish.
   - Read back the room detail with CLI and verify category, product name, hardware model, software version, status, cover, linked entity, tags, and opening message.
   - For a formal vehicle/robot room, also read back the canonical library version data. Do not close the task as complete if the room exists but the library version sync or entity binding is unresolved.
