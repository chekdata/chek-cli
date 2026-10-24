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

## Bring your own Agent

Use the Python CLI in `packages/chek-cli` from an agent that can run local commands (for example Cursor, Codex or Claude Code). Chat-only tools can prepare drafts; they cannot install or execute a CLI merely by receiving a prompt. Follow [chek-setup](skills/chek-setup/SKILL.md), confirm the environment and account, and use ordinary CHEK sign-in.

The hosted MiControl stack, dedicated OpenClaw authorization/device binding, shared tool/skill dispatch and automatic mention replies are retiring in DEV. Existing business APIs, human room notifications, evidence, reviews, scoring, sharing and EGO remain. Stop retrying legacy endpoints on HTTP 410. The TypeScript plugin is migration compatibility only; use the Python CLI for new setup. See [retirement scope](DEPRECATION.md). No staging/production deployment is included.

## Send This To Your Agent

```text
Become my CHEK co-building assistant. First search GitHub for `chekdata/chek-cli`, read `skills/chek-setup`, and help me install and sign in.

CHEK is an AI-native open community for the agent era. It is not asking me to fill forms for a platform. It is helping turn every AI product I try, test, criticize, or love into my own review archive and into public knowledge that helps others choose, re-review, and avoid bad products.

Good products should not be seen only through marketing. Real experience deserves weight.

Help me record the exact hardware model and software version, organize reviews, preserve evidence and ratings, enrich intelligent-vehicle and robot databases, discover new products worth submitting, and turn my ideas into community capabilities.

Rules: check duplicates before submitting; draft first and wait for my confirmation; every review must map to a real hardware model and software version; never leak tokens, codes, cookies, or Authorization headers.

Start now by checking installation and login status, then ask which co-building task I want to begin with.
```

This prompt is both a public invitation and an executable agent brief: it tells a human why participation matters, and tells an agent where to start and what boundaries to keep.

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

The user value is not "helping a platform fill a database." It is building a personal AI-product archive: each real test gets a version, each judgment gets evidence, and each public score has a trail others can re-check.

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

For user-facing distribution, prefer GitHub Release assets or package registries instead of editable installs:

```bash
# pip / pipx: install the Python CLI from the release tag
python -m pip install "git+https://github.com/chekdata/chek-cli.git@v0.5.0#subdirectory=packages/chek-cli"

# Homebrew or internal package sources should point to the v0.5.0 Python release assets and checksums.
```

After installation, verify that the AI product commands are present:

```bash
chek --help
chek manifest
chek ai-product +publish --help
chek media +upload-cover --help
```

Development installs can still use editable mode:

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
chek ai-product +research-plan --category 生产力工具 --product-name Kimi --software-version "2026 年 7 月网页版"
```

## Product Surface

| Product moment | User value | Agent entry point | Operations behind it |
| --- | --- | --- | --- |
| AI product public review | Version-specific review rooms: submit product, collect evidence, rate with stars, and keep re-reviewing. | `ai-product +research-plan`, `+duplicate-check`, `+publish`, `+edit`, `+review`, `media +upload-cover` | `/api/backend-app/buddy/v1/posts`, `duplicate-check`, `reviews`, `backend-app.buddy.posts`, `backend-app.media.images` |
| Driving reports | Turn trip data into safety, efficiency, comfort, and NOA signals users can understand. | `vehicle +buying-plan`, `vehicle +rankings`, `backend-saas report-visualization ...` | `backend-saas.reportVisualization.*`, `backend-saas.noaJour.*`, `backend-saas.journeys.*`, `vehicle.vehicles.detail` |
| Intelligent-driving score | Evidence trails for each tested vehicle, hardware config, and software version. | `vehicle +rankings`, generated `backend-saas app-vehicle-metrics ...` calls | `backend-saas.appVehicleMetrics.rankTop3`, `rankPage`, `modelDetail`, `debugSourceBreakdown` |
| Vehicle leaderboards | City/highway/scene-aware rankings that answer who is strong and why. | `vehicle +rankings` | `backend-saas.appVehicleMetrics.*`, `backend-saas.noaJour.highwayNoaRankTop3`, `backend-saas.options.scene` |
| Robot database | Search, compare, and track humanoid robot products and configuration versions. | `humanoid +search`, `humanoid +compare`, `humanoid +config` | `backend-app.humanoid.leaderboards`, `humanoid.robots.detail`, `humanoid.robots.configVersions`, `humanoid.edits.*` |
| Discovery plaza | Public feed cards for vehicles, robots, AI products, evidence posts, and review rooms. | `discovery +feed` | `backend-app.discovery.feed`, `feedFilters`, `swipeSessions`, `swipeSessionsActions` |
| CHEK CLI co-building | Let your own Agent search, draft, submit, review, rate, and preserve evidence through normal CHEK business APIs. | `ai-product +research-plan`, `+publish`, `vehicle +rankings`, `discovery +feed` | business OpenAPI operations |
| Room collaboration | Keep messages, human @ notifications, unread state, evidence, ratings, sharing, and EGO upload flows. | CHEK web UI or Python CLI | ordinary room and EGO APIs |

## OpenAPI Coverage

The bundled registry is generated from CHEK backend OpenAPI specs.

| Service | What it powers | Resources | Operations |
| --- | --- | ---: | ---: |
| `auth` | login, SMS/password/token auth, user info, scope checks, role/resource APIs, share tokens | 26 | 94 |
| `backend-app` | rooms, mentions, discovery, media, assets, humanoid app views, observability | 25 | 104 |
| `backend-saas` | vehicle metrics, reports, NOA journeys, rankings, report subscriptions, special points | 16 | 91 |
| `crowd` | capture readiness, session catalog, benchmark releases, review queues, public orders | 21 | 267 |
| `humanoid` | robot records, config versions, governance, edits, audit history | 7 | 25 |
| `vehicle` | vehicle search, detail, diff, raw params, software versions, upload/sign flows | 6 | 40 |
| **Total** | Agent-operable CHEK backend surface | **101** | **621** |

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

chek media +upload-cover \
  --file ./cover.png \
  --source-url "https://www.unitree.com/operate/h1/" \
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

## Migration compatibility

Use the Python CLI from your own Agent environment:

```bash
git clone https://github.com/chekdata/chek-cli.git
cd chek-cli/packages/chek-cli
python -m pip install -e ".[dev]"
chek config set-env dev
chek registry status
```

The old TypeScript/OpenClaw package is migration compatibility only. It prints the Python CLI guide and never creates browser-auth sessions, polls mention tasks, or sends automatic room replies.

## Release

Release versions should cover the Python CLI, npm/OpenClaw plugin package, and GitHub Release assets:

```bash
pnpm install
pnpm build
pnpm test

cd packages/chek-cli
python -m pip install -e ".[dev]"
python -m pytest -q tests
python -m build

chek --help
chek ai-product +publish --help
chek media +upload-cover --help
```

After tagging `vX.Y.Z`, publish a GitHub Release and upload:

- root npm tarball, for example `chek-chek-cli-X.Y.Z.tgz`
- Python wheel, for example `chek_cli-X.Y.Z-py3-none-any.whl`
- Python sdist, for example `chek_cli-X.Y.Z.tar.gz`

PyPI, npm, Homebrew taps, and internal package sources should consume the same release version and checksums. If registry tokens such as `PYPI_API_TOKEN` are configured, CI or a release script can continue publishing to the official package registry.

## Repository Note

This repository was formerly `chekdata/memor-upload`. The canonical project is now:

```text
https://github.com/chekdata/chek-cli
```
