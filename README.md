# CHEK CLI

![downloads](https://img.shields.io/github/downloads/chekdata/chek-cli/total?label=downloads)
![phase](https://img.shields.io/badge/phase-agent%20native-0A7D34)
![license](https://img.shields.io/github/license/chekdata/chek-cli)

`CHEK CLI` is the agent operating layer for CHEK. It turns product moments such as "how did this car actually drive?", "ask the assistant with the trip in context", "rank intelligent vehicles by real evidence", "find the robot everyone is watching", and "submit an AI product for public review" into callable, repeatable, auditable CLI commands and OpenAPI operations.

It is not a browser harness that asks an agent to click through a phone UI. It is the control surface underneath the product: publish AI product review rooms, check duplicates, submit star ratings with evidence, search vehicles and robots, pull rankings, create MiControl runs, read discovery feeds, resolve share links, and let OpenClaw answer CHEK room mentions from a local session.

Chinese documentation: [README.zh-CN.md](./README.zh-CN.md).

## Why It Exists

CHEK is becoming a public evidence network for AI products, intelligent vehicles, and robots. Users should not have to guess from marketing copy whether a car's NOA is stable, which robot configuration is current, or whether a software AI product is worth testing. They should see scored reports, versioned reviews, leaderboards, discovery cards, and room discussions that are backed by data and real operations.

CHEK CLI makes that network usable by agents:

- Product users get better reports, rankings, review rooms, and shareable evidence.
- Agents get stable JSON commands instead of fragile UI automation.
- Operators get auth profiles, scoped credentials, registry-backed calls, and raw API fallback.
- Developers get a map from product workflows to the exact backend operations that power them.

## Product Surface

| Product moment | What the user gets | Agent entry point | Operations behind it |
| --- | --- | --- | --- |
| "How did this car drive?" | A driving report that turns trip data into safety, efficiency, comfort, and NOA signals users can understand at a glance. | `vehicle +buying-plan`, `vehicle +rankings`, `backend-saas report-visualization ...` | `backend-saas.reportVisualization.*`, `backend-saas.noaJour.*`, `backend-saas.journeys.*`, `vehicle.vehicles.detail` |
| Intelligent driving score | A score and evidence trail for each tested vehicle/version, not just a brand-level opinion. | `vehicle +rankings`, generated `backend-saas app-vehicle-metrics ...` calls | `backend-saas.appVehicleMetrics.rankTop3`, `rankPage`, `modelDetail`, `debugSourceBreakdown` |
| MiControl assistant | Ask with page, trip, vehicle, or room context; let the assistant turn a vague request into a structured run. | `micontrol create`, `micontrol runs`, `micontrol detail` | `backend-app.micontrol.runs*`, `backend-app.agent.toolsExecute`, `backend-app.agent.toolSessions` |
| Intelligent vehicle leaderboard | City/highway/scene-aware rankings that answer "who is strong, and why?". | `vehicle +rankings` | `backend-saas.appVehicleMetrics.*`, `backend-saas.noaJour.highwayNoaRankTop3`, `backend-saas.options.scene` |
| Discovery plaza | Public feed cards for vehicles, robots, AI products, evidence posts, and review rooms. | `discovery +feed` | `backend-app.discovery.feed`, `feedFilters`, `swipeSessions`, `swipeSessionsActions` |
| Robot leaderboard and database | Search, compare, and track humanoid robot products and configuration versions. | `humanoid +search`, `humanoid +compare`, `humanoid +config` | `backend-app.humanoid.leaderboards`, `humanoid.robots.detail`, `humanoid.robots.configVersions`, `humanoid.edits.*` |
| AI product public review | A Douban-style, version-specific review room: submit product, collect evidence, rate with stars, and keep re-reviewing as the version changes. | `ai-product +research-plan`, `+duplicate-check`, `+publish`, `+edit`, `+review` | `/api/backend-app/buddy/v1/posts`, `duplicate-check`, `reviews`, `backend-app.buddy.posts` |
| Room mentions to local agent | CHEK room `@` mentions become local OpenClaw context, a generated reply, and a room message. | `/chek-setup`, `openclaw chek setup` | `backend-app.buddy.mentionTasks`, `openclawAuthSessions`, `posts/{id}/messages` |
| Shareable evidence | Generate, resolve, or revoke share tokens for anonymous or scoped access. | `share +create`, `share +resolve`, `share +revoke` | `auth.share.token`, `auth.share.resolve`, `auth.share.revoke` |
| Agent identity | Repeatable sessions with the right user/service identity, token, profile, and scope checks. | `config`, `auth`, `auth profile`, `auth credential`, global `--as` | `auth.accounts.*`, `auth.sms.*`, `auth.userInfo`, `auth.validToken`, local profile store |

## Command Surface

Run `chek --help` to inspect the current tree:

```text
ai-product, api, auth, backend-app, backend-saas, build, call, config,
crowd, discovery, doctor, examples, flow, humanoid, manifest, micontrol,
page, registry, repo, routes, schema, serve, share, smoke, vehicle
```

The CLI has three layers:

- **Shortcuts** for high-frequency product work: AI product submission, vehicle planning, rankings, humanoid comparison, discovery feed, share tokens, MiControl runs.
- **Generated OpenAPI commands** for broad backend coverage: `auth`, `backend-app`, `backend-saas`, `crowd`, `humanoid`, and `vehicle`.
- **Fallback primitives** when an agent needs precision: `schema`, `call service.resource.method`, and raw `api METHOD PATH`.

## OpenAPI Coverage

The bundled registry is generated from CHEK backend OpenAPI specs.

| Service | What it powers | Resources | Operations |
| --- | --- | ---: | ---: |
| `auth` | login, SMS/password/token auth, user info, scope checks, role/resource APIs, share tokens | 25 | 86 |
| `backend-app` | rooms, mentions, discovery, media, assets, MiControl, humanoid app views, observability | 27 | 135 |
| `backend-saas` | vehicle metrics, reports, NOA journeys, rankings, report subscriptions, special points | 14 | 85 |
| `crowd` | capture readiness, session catalog, benchmark releases, review queues, public orders | 7 | 127 |
| `humanoid` | robot records, config versions, governance, edits, audit history | 6 | 21 |
| `vehicle` | vehicle search, detail, diff, raw params, software versions, upload/sign flows | 6 | 39 |
| **Total** | Agent-operable CHEK backend surface | **85** | **493** |

Useful registry and raw-call commands:

```bash
chek registry status
chek schema vehicle.vehicles.batchSearch
chek call vehicle.vehicles.detail --path id=veh_123 --dry-run
chek vehicle vehicles batch-search \
  --data '{"queries":[{"query":"小米 SU7"}]}' \
  --dry-run
chek api GET /api/backend-app/login/checkToken --dry-run
```

## Quick Start

The Python CLI emits JSON by default. `--json` is kept as a compatibility alias for `--format json`.

```bash
cd packages/chek-cli
python -m pip install -e ".[dev]"

chek config set-env dev
chek config default-as user
chek auth login --method token --token "$CHEK_ACCESS_TOKEN" --profile dev-agent
chek registry status
chek manifest
```

Try the product workflows in dry-run mode:

```bash
chek ai-product +research-plan \
  --category 生产力工具 \
  --product-name Kimi \
  --software-version "2026 年 7 月网页版"

chek vehicle +buying-plan \
  --query "小米 SU7" \
  --scene urban \
  --city 上海 \
  --dry-run

chek vehicle +rankings --scene urban --window latest --dry-run
chek humanoid +search --query "Unitree" --page-size 10 --dry-run
chek discovery +feed --q "AI 产品" --dry-run
chek micontrol create --task "帮我分析这次智驾报告" --dry-run
```

## AI Product Review Rooms

The AI product workflow is version-specific:

```text
Public product submission -> all users review -> 5 valid Sun Chaser reviews -> public score -> continuous re-review
```

The duplicate-check identity tuple is:

```text
category + product name + hardware model + software version
```

Pure software products can leave `--hardware-model` empty, but `--software-version` is required because rankings and reviews must point to a specific version. That is the difference between reviewing "Kimi" and reviewing "Kimi, 2026 July web version".

Research before submitting:

```bash
chek ai-product +research-plan \
  --category 生产力工具 \
  --product-name Kimi \
  --software-version "2026 年 7 月网页版"
```

Check duplicates:

```bash
chek ai-product +duplicate-check \
  --category 具身机器人 \
  --product-name "Unitree G1" \
  --hardware-model EDU \
  --software-version v1.2.4 \
  --dry-run
```

Publish after research and duplicate check:

```bash
chek ai-product +publish \
  --category 生产力工具 \
  --product-name Kimi \
  --software-version "2026 年 7 月网页版" \
  --tag 长文本 \
  --reason "值得复评长文本能力" \
  --scenario "办公、学习、资料整理" \
  --source-url "https://example.com/source" \
  --dry-run
```

`+publish` stops by default when the same version tuple already exists. Use the matched room from the output to keep reviewing the existing room, or explicitly pass `--duplicate-policy allow`.

Edit an existing room:

```bash
chek ai-product +edit \
  --post-id <room_uuid> \
  --software-version "2026 年 7 月网页版" \
  --reason "补充新一轮复评理由" \
  --dry-run
```

Submit or update a star rating with evidence:

```bash
chek ai-product +review \
  --post-id <room_uuid> \
  --stars 4.5 \
  --comment "长文本总结稳定，版本已确认" \
  --evidence "附测试记录和截图链接" \
  --evidence-url "https://example.com/evidence"
```

Browse rooms:

```bash
chek ai-product +list --scope public --dry-run
chek ai-product +detail --post-id <room_uuid> --dry-run
```

## Vehicles And Driving Reports

CHEK's vehicle operations are built for questions real users ask:

- "This car looks good, but how does it behave in real trips?"
- "Is its NOA still experimental, or is it stable enough to trust?"
- "How does it compare with another model in urban, highway, safety, and comfort scenes?"
- "Which version, hardware config, and software config was actually tested?"

Common commands:

```bash
chek vehicle +search --query "星途 ET5" --top-k 10 --dry-run
chek vehicle detail --id <vehicle_id> --dry-run
chek vehicle raw-params --id <vehicle_id> --dry-run
chek vehicle +compare --id <vehicle_1> --id <vehicle_2> --include-raw --include-software --dry-run
chek vehicle +rankings --scene urban --window latest --dry-run
```

Generated operations let agents go deeper into report data:

```bash
chek backend-saas app-vehicle-metrics rank-top3 --param scene=urban --dry-run
chek backend-saas report-visualization query-urban-report-indicator --params '{"vehicleId":"veh_123"}' --dry-run
chek backend-saas noa-jour noa-indicators --params '{"vehicleId":"veh_123"}' --dry-run
```

## Robots And Embodied AI

Humanoid and robot operations make the robot database more than a list of names. Agents can search the market, compare models, inspect configuration versions, and connect app leaderboards with canonical robot records.

```bash
chek humanoid +search --query "Unitree" --page-size 10 --dry-run
chek humanoid +compare --id robot_1 --id robot_2 --dry-run
chek humanoid +config --id robot_1 --dry-run
chek backend-app humanoid leaderboards --dry-run
```

This is the operation layer behind "robot leaderboard" and "who is becoming the top robot in the circle?" product surfaces.

## OpenClaw Plugin

Install the plugin:

```bash
openclaw plugins install 'https://github.com/chekdata/chek-cli/archive/refs/heads/main.tar.gz?download=1'
```

OpenClaw-facing commands:

```text
/chek-setup
/chek-status
/chek-bootstrap
```

CLI equivalents:

```bash
openclaw chek setup
openclaw chek status
openclaw chek bootstrap
```

The default setup path uses browser authorization. If browser auth fails, token setup remains available:

```text
/chek-setup token=<CHEK_ACCESS_TOKEN>
```

```bash
openclaw chek setup --token <CHEK_ACCESS_TOKEN>
```

After setup, the plugin can create browser-auth sessions, persist stable install/device IDs, poll CHEK room `@` mention tasks, load recent room context, inject that context into a local OpenClaw session, generate a reply, send the reply back to the CHEK room, and complete or fail the mention task.

Intent handling currently covers setup/bootstrap, posting copy, listing readiness, value judgement, appeal judgement, clarity judgement, download troubleshooting, distribution choice, and generic room replies.

## Auth And Profiles

The CLI stores config under `~/.chek-cli` by default. Set `CHEK_CLI_HOME` to isolate an agent session.

```bash
chek config show
chek config set-env dev
chek config set-origin https://api-dev.chekkk.com/api/backend-app
chek config default-as user
chek config secret-store keyring
```

Supported login and credential helpers:

```bash
chek auth login --method token --token "$CHEK_ACCESS_TOKEN" --profile dev-agent
chek auth sms-send --phone "13800000000"
chek auth login --method sms --phone "13800000000" --code "123456" --profile dev-agent
chek auth login --method password --phone "13800000000" --password "$CHEK_PASSWORD"
chek auth credential set --profile dev-agent --identity service --token "$CHEK_SERVICE_TOKEN"
chek --as service auth status
chek auth check --scope vehicle:read --verify
```

Named profiles let agents switch between environments or accounts:

```bash
chek auth profile list
chek auth profile save dev-agent --activate
chek auth profile use dev-agent
chek auth profile export dev-agent --output ./dev-agent.profile.json
chek auth profile import dev-agent --file ./dev-agent.profile.json --activate
```

## Bundled Skills

- [`skills/chek-setup/SKILL.md`](./skills/chek-setup/SKILL.md): helps OpenClaw finish CHEK CLI setup, browser authorization, fallback token setup, and health checks.
- [`skills/chek-ai-product-sourcing/SKILL.md`](./skills/chek-ai-product-sourcing/SKILL.md): helps agents source, verify, classify, dedupe, and package CHEK AI product candidates before formal CLI submission. It writes either local artifacts or a user-specified Feishu/Lark candidate base; no default candidate base is hard-coded.

## Frontend And Evidence Helpers

These commands are auxiliary. They help agents collect repo, route, H5 build, page, and smoke-flow evidence when a visual or local app check is needed.

```bash
chek doctor
chek repo status
chek routes list
chek routes find product
chek serve h5 --port 10086 --wait-seconds 60
chek page url /pages/index/index --base-url http://localhost:10086
chek page snapshot /pages/index/index --base-url http://localhost:10086 --output ./page.png
chek flow smoke --url http://localhost:10086 --retries 10 --interval 2
chek build h5 --dry-run
```

Runtime pid/log files are written under `.agent-harness/run/` in the repository root and are intentionally git-ignored.

## Examples And Smoke

```bash
chek examples list
chek examples show vehicle.buying-plan
chek examples generate --service vehicle --resource vehicles --limit 5
chek manifest --include-operations --operation-limit 20
chek smoke api --dry-run
chek smoke auth --dry-run
chek smoke api --include-authenticated --include-auth-check
```

## Install For Development

```bash
cd packages/chek-cli
python -m pip install -e ".[dev]"
```

Optional browser and frontend evidence helpers:

```bash
python -m pip install -e ".[browser,dev]"
python -m playwright install chromium
```

Local OpenClaw plugin development:

```bash
openclaw plugins install --link /absolute/path/to/chek-cli
```

## Regenerate OpenAPI Registry

```bash
cd packages/chek-cli
python scripts/generate_openapi_registry.py
```

The generator pulls dev gateway OpenAPI for `auth`, `backend-app`, `vehicle`, `crowd`, and `humanoid`. If `backend-saas` is not exposed through the gateway, export it from that repo with Java 17 and pass it explicitly:

```bash
JAVA_HOME=$(/usr/libexec/java_home -v 17) bash scripts/export_openapi.sh
python scripts/generate_openapi_registry.py \
  --source backend-saas=/path/to/backend-saas/build/swagger/backend-saas-openapi.json
```

CI also runs `scripts/check_registry_drift.py --allow-missing-optional`. Set `CHEK_BACKEND_SAAS_OPENAPI` when a backend-saas OpenAPI file or URL is available.

## Repository Layout

- `packages/chek-cli`: Python CHEK CLI package and generated OpenAPI registry.
- `packages/chek-cli/README.md`: package-level CLI reference.
- `src/index.ts`: OpenClaw plugin entry.
- `src/commands.ts`: `/chek-setup`, `/chek-status`, `/chek-bootstrap`, and OpenClaw CLI commands.
- `src/service.ts`: background polling loop, browser auth sync, mention task processing, and room reply orchestration.
- `src/render.ts`: room-context compaction, intent detection, direct replies, and local prompt construction.
- `skills/chek-setup/SKILL.md`: bundled setup skill.
- `skills/chek-ai-product-sourcing/SKILL.md`: bundled AI product sourcing skill.
- `docs/bootstrap-message.md`: user-facing bootstrap copy.
- `docs/device-code-auth.md`: browser-auth flow and fallback rules.
- `docs/troubleshooting.md`: common failure paths.

## Development

```bash
pnpm install
pnpm build
pnpm test

cd packages/chek-cli
python -m pip install -e ".[dev]"
python -m pytest -q tests
```

## Release

Tag releases build wheel/sdist artifacts through GitHub Actions. If `PYPI_API_TOKEN` is configured, tagged releases publish to PyPI. The repository also includes a Dockerfile:

```bash
docker build -t chek-cli .
docker run --rm chek-cli manifest
```

## Repository Note

This repository was formerly `chekdata/memor-upload`. The canonical project is now:

```text
https://github.com/chekdata/chek-cli
```
