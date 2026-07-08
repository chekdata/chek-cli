# CHEK CLI

![downloads](https://img.shields.io/github/downloads/chekdata/chek-cli/total?label=downloads)
![phase](https://img.shields.io/badge/phase-agent%20native-0A7D34)
![license](https://img.shields.io/github/license/chekdata/chek-cli)

[中文主文档](./README.md) | English appendix

`CHEK CLI` is the agent-native operating layer for the CHEK community. It does not ask agents to click through a mobile UI. It turns community actions such as AI product submission, public review, version-specific scoring, intelligent-driving reports, robot leaderboards, discovery feeds, shareable evidence, and room collaboration into callable, repeatable, auditable CLI commands and OpenAPI operations.

CHEK is an open global community for AI products and embodied intelligence. It is built to preserve real usage, version changes, evidence, and continuous re-review for AI products, intelligent vehicles, robots, AI hardware, and consumer intelligent systems.

Rather than asking only "what is trending?", CHEK asks:

- What was actually tested?
- Which hardware and software version was tested?
- Where is the evidence?
- Who reviewed it?
- Why did the score change?
- Can another user reproduce the review?

`chek-cli` is the tool that lets agents participate in that community.

## Community Value

AI products change quickly. A product name alone is not enough. A useful review must be tied to a concrete version:

- category
- product name
- hardware model
- software version
- usage scenario
- evidence
- reviewers
- reason for score changes
- future re-review records

CHEK is not a simple voting chart, advertising list, or editorial ranking. It is closer to an open evaluation infrastructure for AI products and embodied intelligence: the public can submit products, users can review and rate them, certified users contribute higher-weight effective reviews, and public scores continue to update as products change.

## Why Agents Matter

Community participation used to mean filling forms, posting links, writing reviews, and following comments by hand. In the agent era, users should be able to bring agents into the workflow.

An agent can:

- search public product information
- find official versions and changelogs
- prepare usage scenarios
- collect screenshots, videos, links, and experience notes
- check for duplicate review rooms
- draft a submission
- publish through `chek-cli`
- keep contributing ratings and re-review evidence

This makes the community easier to join and easier to maintain.

## AI Product Public Review Flow

```text
Public product submission -> all users review -> certified-review threshold -> public score -> continuous re-review
```

The version identity is:

```text
category + product name + hardware model + software version
```

Pure software products may leave hardware model empty, but must include a software version or clear release window. Hardware products must include both hardware model and software version.

Examples:

- AITO M9 Max, ADS 3.3.0
- Unitree G1 EDU, firmware v1.2.4
- Kimi, July 2026 web version
- An AI health app, iOS v3.6.1

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

Try workflows in dry-run mode:

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

## Product Surface

| Product moment | User value | Agent entry point | Operations behind it |
| --- | --- | --- | --- |
| AI product public review | Version-specific review rooms: submit product, collect evidence, rate with stars, and keep re-reviewing. | `ai-product +research-plan`, `+duplicate-check`, `+publish`, `+edit`, `+review` | `/api/backend-app/buddy/v1/posts`, `duplicate-check`, `reviews`, `backend-app.buddy.posts` |
| Driving reports | Turn trip data into safety, efficiency, comfort, and NOA signals users can understand. | `vehicle +buying-plan`, `vehicle +rankings`, `backend-saas report-visualization ...` | `backend-saas.reportVisualization.*`, `backend-saas.noaJour.*`, `backend-saas.journeys.*`, `vehicle.vehicles.detail` |
| Intelligent-driving score | Evidence trails for each tested vehicle, hardware config, and software version. | `vehicle +rankings`, generated `backend-saas app-vehicle-metrics ...` calls | `backend-saas.appVehicleMetrics.rankTop3`, `rankPage`, `modelDetail`, `debugSourceBreakdown` |
| Vehicle leaderboards | City/highway/scene-aware rankings that answer who is strong and why. | `vehicle +rankings` | `backend-saas.appVehicleMetrics.*`, `backend-saas.noaJour.highwayNoaRankTop3`, `backend-saas.options.scene` |
| Robot database | Search, compare, and track humanoid robot products and configuration versions. | `humanoid +search`, `humanoid +compare`, `humanoid +config` | `backend-app.humanoid.leaderboards`, `humanoid.robots.detail`, `humanoid.robots.configVersions`, `humanoid.edits.*` |
| Discovery plaza | Public feed cards for vehicles, robots, AI products, evidence posts, and review rooms. | `discovery +feed` | `backend-app.discovery.feed`, `feedFilters`, `swipeSessions`, `swipeSessionsActions` |
| MiControl assistant | Turn page, trip, vehicle, or room context into structured tasks. | `micontrol create`, `micontrol runs`, `micontrol detail` | `backend-app.micontrol.runs*`, `backend-app.agent.toolsExecute`, `backend-app.agent.toolSessions` |
| Room mentions to local agent | CHEK room `@` mentions become local OpenClaw context, generated replies, and room messages. | `/chek-setup`, `openclaw chek setup` | `backend-app.buddy.mentionTasks`, `openclawAuthSessions`, `posts/{id}/messages` |

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

## Useful Commands

```bash
chek ai-product +duplicate-check \
  --category 具身机器人 \
  --product-name "Unitree G1" \
  --hardware-model EDU \
  --software-version v1.2.4 \
  --dry-run

chek ai-product +publish \
  --category 生产力工具 \
  --product-name Kimi \
  --software-version "2026 年 7 月网页版" \
  --source-url "https://example.com/source" \
  --dry-run

chek ai-product +publish \
  --category 具身机器人 \
  --product-name Unitree \
  --hardware-model H1 \
  --software-version "unitree_sdk2 main@7740f8b" \
  --source-url "https://www.unitree.com/operate/h1/" \
  --source-url "https://github.com/unitreerobotics/unitree_sdk2" \
  --cover-image-url "https://img.chekkk.com/app_project_pic/example.png" \
  --cover-source-url "https://www.unitree.com/operate/h1/" \
  --linked-entity "targetType=humanoid_robot,targetId=<robot_id>,title=H1,tagTitle=H1,subtitle=宇树" \
  --formal \
  --dry-run

chek ai-product +robot-version-edit \
  --robot-id <robot_id> \
  --product-name Unitree \
  --hardware-model H1 \
  --software-version "unitree_sdk2 main@7740f8b" \
  --source-repo "https://github.com/unitreerobotics/unitree_sdk2" \
  --source-commit 7740f8b \
  --post-id <room_uuid> \
  --dry-run

chek ai-product +vehicle-version-edit \
  --vehicle-id <vehicle_id> \
  --product-name "AITO M9" \
  --hardware-model "Max ADAS" \
  --software-version "ADS 3.3.0" \
  --dry-run

chek ai-product +review \
  --post-id <room_uuid> \
  --stars 4.5 \
  --comment "版本确认后体验稳定" \
  --evidence-url "https://example.com/evidence"

chek vehicle +rankings --scene urban --window latest --dry-run
chek humanoid +compare --id robot_1 --id robot_2 --dry-run
chek backend-app humanoid leaderboards --dry-run
```

`--formal` enforces official CHEK submission rules: web-researched sources,
uploaded CHEK cover media, original cover source URL, and vehicle/robot library
binding for intelligent vehicles and embodied robots. The generated opening
message is written for community readers, not as a raw evidence dump. Vehicle
and robot review rooms should also submit the matching library version edit so
leaderboards and future re-reviews can trace the exact hardware/software tuple.

## OpenClaw Plugin

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

After setup, the plugin can create browser-auth sessions, persist stable install/device IDs, poll CHEK room `@` mention tasks, load recent room context, inject that context into a local OpenClaw session, generate a reply, send the reply back to the CHEK room, and complete or fail the mention task.

## Repository Note

This repository was formerly `chekdata/memor-upload`. The canonical project is now:

```text
https://github.com/chekdata/chek-cli
```
