# CHEK AI Product Candidate Base Reference

## Output Target Selection

Do not assume or hard-code a default Feishu Base. At the start of a run, determine the output target:

- Local output: write Markdown, CSV, JSON, or a combination requested by the user in the current workspace.
- Feishu/Lark output: write only to the Base or Wiki explicitly supplied by the user for this run.

If the user has not specified a target, ask one concise question before writing: local output or a user-specified Feishu/Lark candidate Base.

If the user supplies a Feishu wiki link, resolve the wiki node first and use the resolved Base token. Do not assume the URL token is the Base token.

The previously used project candidate Base must remain masked in reusable documentation as `Lgpp…nYb / tbl…pJe`; never expand or persist exact IDs in this skill.

## Field Set

Use this field set for either local output or Feishu output:

- `产品名`
- `类别`
- `类型`
- `状态`
- `重点`
- `硬件型号`
- `软件版本`
- `标签`
- `国内获取`
- `证据来源`
- `提报内容`
- `待补材料`
- `统计时间窗口口径`
- `月度依据`
- `搜索日期`

Do not add fields for routine work. The user prefers fewer, simpler columns. For local output, use these as table/CSV/JSON keys.

## Categories

Use these categories:

- `智能汽车`
- `具身机器人`
- `生产力工具`
- `AI 健康应用`
- `其他消费级 AI 产品`

## Status Labels

- `建议提报`: Product is public-facing, source-backed, consumer-usable, versionable, and likely worth formal submission.
- `待实测材料`: Product is promising and accessible enough to evaluate, but needs screenshots, app/version proof, real-device logs, videos, or first-hand test evidence.
- `待渠道确认`: Product is relevant but purchase, trial, borrow, public beta, or domestic access is not proven.
- `待证据确认`: Product has a plausible AI feature, but current sources do not yet prove the exact AI entrance, version, release window, or safety boundary.
- `观察暂缓`: Product is interesting but not suitable for near-term domestic candidate submission because of access limits, weak AI fit, old/non-window timing, or insufficient evidence.

Avoid vague bulk labels such as "待补材料 29". Use actionable status and precise `待补材料`.

## Type Labels

Use existing options when available:

- `月度新发布`
- `重大版本更新`
- `热度爆发`
- `观察待补`

Do not reintroduce `类目基准`.

## Time Window Tags

Use the existing `统计时间窗口口径` multi-select values:

- `月度窗:2026-05-01~2026-06-01`
- `季度窗:2026-03-15~2026-06-15`
- `6月更新窗:2026-06-01~2026-07-01`
- `观察/非当期`

When the user says to search with a larger window, search by the quarterly window. Monthly tags can still be added when a product also qualifies.

## Version Rules

- Pure software: `硬件型号` may be blank/null; `软件版本` must include app/web/model version or date-specific web version.
- Cars: include exact vehicle trim, ADAS/system/OTA version, cockpit OS, model supplier, and screenshot requirements.
- Robots: include hardware SKU, robot firmware, app version, SDK version, and real-device test requirements.
- Glasses and AI hardware: include exact hardware SKU, app/firmware version, paired phone system when relevant, and privacy/safety notes.
- Health: include app version, AI entrance, disclaimer, AI vs doctor boundary, privacy/data deletion notes, and red-flag symptom test requirements.

## Local Output

For local output, create a file in the current workspace. Use the same fields listed above.

Recommended names:

- `ai-product-candidates-YYYYMMDD.md`
- `ai-product-candidates-YYYYMMDD.csv`
- `ai-product-candidates-YYYYMMDD.json`

Prefer Markdown when the user wants review, CSV when the user wants spreadsheet import, and JSON when another tool or CLI will consume the data.

## Feishu Commands

Use these only after the user supplies the target Base/Wiki/table. Replace placeholders with user-provided or resolved values.

Read fields:

```bash
lark-cli base +field-list \
  --base-token <BASE_TOKEN> \
  --table-id <TABLE_ID> \
  --offset 0 \
  --limit 100
```

Read records:

```bash
lark-cli base +record-list \
  --base-token <BASE_TOKEN> \
  --table-id <TABLE_ID> \
  --offset 0 \
  --limit 200
```

Write a record:

```bash
lark-cli base +record-upsert \
  --base-token <BASE_TOKEN> \
  --table-id <TABLE_ID> \
  --json '{"产品名":"示例产品","类别":"生产力工具","状态":"建议提报"}'
```

Use `+data-query` for counts. Do not hand-count pulled records when service-side aggregation is available.

## Record Writing Pattern

For each new candidate, fill:

- `产品名`: public product name.
- `类别`: one category from the category list.
- `类型`: release/update/observation type.
- `状态`: actionable status label.
- `重点`: `是`, `待定`, or `否`.
- `硬件型号`: precise hardware model, or blank for pure software.
- `软件版本`: app/model/firmware/vehicle system version, with date.
- `标签`: concise comma-separated tags for matching and discovery.
- `国内获取`: domestic availability and access route. Use cautious wording.
- `证据来源`: source URLs and evidence conclusion.
- `提报内容`: reason, scenarios, and interest relationship in content form.
- `待补材料`: exact missing evidence, screenshots, videos, logs, or channel confirmations.
- `统计时间窗口口径`: one or more existing time-window options.
- `月度依据`: explain why it qualifies and any known uncertainty.
- `搜索日期`: current local timestamp.

## Priority Shortlist Pattern

When the user asks to execute the next step after sourcing, mark a small evidence-collection shortlist without adding fields:

- `重点`: set to `是` for P0/P1 records that need active follow-up.
- `待补材料`: start with `P0 实测任务包 - <product>` or `P1 横评/复评任务包 - <product>`.
- `月度依据`: start with `P0优先实测`, `P0复评`, `P1横评样本`, or `P1复评`, then explain why.
- `状态`: keep the actionable status. Use `待实测材料` when the candidate is promising but lacks first-hand screenshots/videos/logs. Do not mark `建议提报` solely because Zhihu has discussion heat.

Use `P0` for:

- current-window products with official availability plus strong review value;
- products with real user discussion and clear domestic access;
- major version or feature changes that can materially alter a prior score.

Use `P1` for:

- comparison samples for a P0 product;
- non-window but useful baseline products;
-复评跟随项 where official proof is still weak;
- candidates that need channel confirmation before formal submission.

For复评, keep the original candidate row unless the product/version tuple has fundamentally changed. Add dated evidence requirements to `待补材料` and explain in `月度依据` that the update is a复评 variable, not a new product.

## Miss Pattern Notes

Known miss patterns from prior work:

- `上汽大众 ID. ERA 9X` was missed because search focused on 华为/小米/城市NOA/激光雷达 and did not cover `Momenta R7`, `世界模型`, `合资品牌`, or 上汽大众 naming.
- `广汽埃安 N60` was missed until searching `文远知行`, `GENESIS`, and `ADiGO`.
- AI glasses and AI recorder hardware can be missed when searching only App Store or software names.
- AI health platform entrances can be missed when searching only independent apps.
- Home appliance and companion robot products can be missed when searching only humanoids or developer robots.

Use brand/ecosystem/supplier/form-factor expansion whenever the user asks if the list is incomplete.
