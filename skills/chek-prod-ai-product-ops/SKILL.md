---
name: chek-prod-ai-product-ops
description: Production-only CHEK AI product operations for formal review-room publication, duplicate checks, cover upload/source auditing, vehicle/robot entity binding, version edit submissions, review evidence posting, approval checks, and long-term humanoid/robot database maintenance. Use when the user asks to operate CHEK prod, submit official AI product reviews, maintain robot database facts, enrich sales/open-source leaderboard support, or keep vehicle/robot versions synchronized through chek-cli.
---

# CHEK Prod AI Product Ops

## Non-Negotiable Environment Rule

Operate **prod only**.

- Use this skill only against CHEK production. Do not use dev, staging, `api-dev.chekkk.com`, DEV login homes, or DEV share links.
- Before any API read or write, verify the CLI target is prod with `chek config show` and `chek auth status --check`.
- If the configured origin contains `api-dev`, `dev`, or a temporary DEV home such as `/tmp/chek-cli-dev-*`, stop and switch to a prod profile or ask for prod credentials.
- Do not print access tokens, SMS codes after use, cookies, or Authorization headers.

## Reference Routing

Read [references/prod-cli-runbook.md](references/prod-cli-runbook.md) before running formal prod submissions, room edits, reviews, approvals, or media upload work.

Read [references/robot-database-maintenance.md](references/robot-database-maintenance.md) before maintaining robot records, config versions, sales facts, price facts, open-source resources, or leaderboard support data.

## Core Workflow

1. **Prod preflight**
   - Verify prod environment, authenticated user, and permission scope.
   - Record the intended mutation: publish room, update room, submit robot edit, submit vehicle edit, approve edit, or post evidence.
   - For destructive actions or approvals, require an explicit user instruction for that action.

2. **Research and identity lock**
   - Browse current official and reliable sources.
   - Lock the version tuple: category, product name, hardware model, software/system/SDK/firmware version.
   - For pure software, hardware may be empty, but software version must be specific.
   - For vehicles and robots, hardware and software version are required.

3. **Library binding**
   - Search CHEK robot or vehicle library before publishing.
   - Bind `linkedEntities` and tags to the canonical robot/vehicle entity.
   - If the main entry does not exist, do not publish an unbound review room; create or report a missing-main-entry task.

4. **Formal room submission**
   - Use `chek ai-product +publish --formal`.
   - Provide web sources, CHEK-uploaded cover URL, original cover source URL, and linked entity.
   - Keep room text readable: explain what is being reviewed, why it matters, and how users should participate.
   - Do not paste search logs or raw evidence dumps into the first message.

5. **Version synchronization**
   - Robots: submit `chek ai-product +robot-version-edit`.
   - Vehicles: submit `chek ai-product +vehicle-version-edit`.
   - Link the edit to the room `post-id` whenever possible.
   - Leave approved/pending/rejected status explicit in the final report.

6. **Long-term database maintenance**
   - Maintain robot profile, config versions, sales facts, price facts, open-source resources, and evidence quality.
   - Prefer edit submissions over direct writes unless the CLI command is explicitly a governed admin action.
   - Keep leaderboard support explainable: sales facts for sales ranking, community rooms for heat ranking, open-source resources plus room activity for open-source ranking.

## Room Content Standard

Use clean, community-facing language:

```text
我们正在评审 <产品 硬件型号> 这个具体版本。
软件/系统版本：<版本>

这不是泛评品牌，而是看这一版在真实场景里是否好用、稳定、值得推荐。

为什么值得测：<1-2 句用户能理解的价值>

建议先看：
- <评审维度 1>
- <评审维度 2>
- <评审维度 3>

用过这一版、跑过资料或能补充可靠证据的朋友，都可以进来打星和补体验。
```

Title format:

```text
<产品名> <硬件型号>，<软件/系统版本>
```

Avoid titles like `资料整理`, `榜单支撑`, `开源材料`, `2026-xx-xx 搜索结果`, or anything that describes the agent's process rather than the reviewed product version.

## Evidence Policy

- Use official pages, product pages, release notes, app stores, manufacturer media, store pages, GitHub repos, papers, trusted media, and first-hand test evidence.
- Use Zhihu Developer search as Chinese discussion/evaluation evidence, not as the sole source for release date, version, availability, or sales facts.
- For cover images, record both the CHEK media URL and the original web source URL.
- For sales facts, record month, units, confidence, source title, source URL, and whether the source is official, channel estimate, or media/reporting.
- For open-source resources, record resource type, platform, URL, repo name if applicable, stars/forks if available, version linkage, confidence, and source date.

## Final Report Checklist

After prod work, report:

- Prod environment verified.
- Room IDs created or updated.
- Duplicate check result.
- Linked robot/vehicle entity IDs.
- Cover source and CHEK media URL status.
- Robot/vehicle version edit submission IDs and status.
- Any approvals performed.
- Remaining missing evidence or main-entry gaps.
