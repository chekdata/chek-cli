# CHEK CLI

English | [中文](README.zh-CN.md)

Agent-native CLI for CHEK product publication, review rooms, and backend capabilities.

CHEK CLI turns CHEK backend capabilities into an interface that AI agents can
use directly: publish AI product review rooms, check duplicates, submit ratings
with evidence, discover schemas, call generated OpenAPI commands, run stable
shortcuts, authenticate, and fall back to raw API calls when needed.

## Product Positioning

CHEK CLI is the agent entry point for building:

- AI product review rooms: public product submission, web-researched evidence, duplicate checks, rating, and ongoing re-review.
- Car-buying OpenClaw (买车 OpenClaw): agent workflows for finding, comparing, explaining, and acting on vehicle choices.
- AI-native Autohome (AI 版汽车之家): an agent-first vehicle research and decision interface, not just a human browsing UI.
- Dongjidi-style intelligence (懂机帝): structured specs, rankings, comparisons, and explainable recommendations for machines.
- Robot database: queryable robot product, market, and evidence data.
- Intelligent vehicle database: canonical vehicle metadata, versions, raw parameters, rankings, releases, and edit/audit workflows.
- Humanoid robot configuration data: humanoid robot models, versions, config snapshots, governance parameters, leaderboards, and edit history.

Brand names above are positioning shorthand only. This project is not affiliated with third-party brands.

## Why A CLI

The CLI follows the lark-cli pattern rather than a browser-harness pattern:

- Shortcuts for high-frequency agent jobs.
- OpenAPI-generated command trees for broad backend coverage.
- `schema` and `call` for precise service/resource/method invocation.
- Raw `api METHOD PATH` for full fallback coverage.
- `config` and `auth` for repeatable agent sessions.
- Optional frontend helpers only when visual/build evidence is needed.

## Install

```bash
python -m pip install -e ".[dev]"
```

Optional browser/dev helpers:

```bash
python -m pip install -e ".[browser,dev]"
python -m playwright install chromium
```

## Quick Start

JSON is the default output format. `--json` is kept as a compatibility alias.

```bash
chek config show
chek config set-env dev
chek config default-as user
chek auth status
chek auth login --method token --token "$CHEK_ACCESS_TOKEN" --profile dev-agent
chek registry status
chek manifest

chek ai-product +research-plan \
  --category 生产力工具 \
  --product-name Kimi \
  --software-version "2026 年 7 月网页版"
```

AI product publish/review examples:

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
  --reason "值得复评长文本能力" \
  --scenario "办公、学习、资料整理" \
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

chek ai-product +review \
  --post-id <room_uuid> \
  --stars 4.5 \
  --comment "版本确认后体验稳定" \
  --evidence-url "https://example.com/evidence" \
  --dry-run
```

`--formal` enforces official CHEK submission rules: web-researched sources,
uploaded CHEK cover media, original cover source URL, and vehicle/robot library
binding for intelligent vehicles and embodied robots. The generated opening
message is written for community readers, not as a raw evidence dump.

Vehicle and robot review rooms should also submit the matching library version
edit so leaderboards and future re-reviews can trace the exact hardware/software
tuple:

```bash
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
```

Vehicle and ranking examples:

```bash
chek vehicle +buying-plan --query "小米 SU7" --scene urban --city 上海 --dry-run
chek vehicle +compare --id veh_1 --id veh_2 --include-raw --dry-run
chek vehicle +rankings --scene urban --window latest --dry-run

chek schema vehicle.vehicles.batchSearch
chek vehicle vehicles batch-search \
  --data '{"queries":[{"query":"小米 SU7"}]}' \
  --dry-run

chek backend-saas app-vehicle-metrics rank-top3 \
  --param scene=urban \
  --dry-run
```

Humanoid robot examples:

```bash
chek humanoid +search --query "Unitree" --page-size 10 --dry-run
chek humanoid +compare --id robot_1 --id robot_2 --dry-run
chek humanoid +config --id robot_1 --dry-run

chek schema humanoid.robots.configVersions
chek humanoid robots config-versions \
  --id robot_123 \
  --dry-run
```

Raw fallback examples:

```bash
chek call vehicle.vehicles.detail --path id=veh_123 --dry-run
chek api GET /api/backend-app/login/checkToken --dry-run
```

## Command Layers

| Layer | Commands | Purpose |
| --- | --- | --- |
| Shortcuts | `ai-product +publish`, `ai-product +review`, `vehicle +buying-plan`, `vehicle +compare`, `vehicle +rankings`, `humanoid +compare`, `discovery +feed`, `share +resolve` | Stable high-level workflows for agents |
| OpenAPI tree | `vehicle vehicles batch-search`, `backend-app agent skills-run`, `humanoid robots detail` | Generated service/resource/method commands |
| API commands | `schema`, `call`, `api` | Discovery, registry-backed calls, and raw backend fallback |
| Session | `--as auto/user/service/none`, `config default-as`, `auth`, `auth profile`, `auth credential` | Lark-style identity switching, API origin, token, profile, and credential management |
| Discovery and checks | `examples`, `smoke api`, `registry status` | Generated examples, read-only backend smoke checks, and registry coverage |
| Dev helpers | `doctor`, `repo`, `routes`, `serve`, `build`, `page`, `flow` | Optional frontend repo/build/browser diagnostics |

The bundled registry is generated from backend OpenAPI specs and currently
covers 6 services and 493 operations: `auth`, `backend-app`, `backend-saas`,
`crowd`, `humanoid`, and `vehicle`.

```bash
chek registry status
```

## Auth

The CLI stores local config under `~/.chek-cli` by default. Set
`CHEK_CLI_HOME` to isolate a session.

```bash
chek config set-env dev
chek config default-as user
chek auth login --method token --token "$CHEK_ACCESS_TOKEN" --profile dev-agent
chek auth status --check
```

The credential model follows the Lark CLI shape: choose an identity with
`--as`, set a default with `config default-as`, and keep credentials in named
profiles. CHEK identities are `user`, `service`, `auto`, and `none`.

Supported login and credential helpers:

```bash
chek auth sms-send --phone "13800000000"
chek auth login --method sms --phone "13800000000" --code "123456" --profile dev-agent
chek auth login --method password --phone "13800000000" --password "$CHEK_PASSWORD"
chek auth credential set --profile dev-agent --identity service --token "$CHEK_SERVICE_TOKEN"
chek --as service auth status
chek auth check --scope vehicle:read --verify
```

Named profiles let agents switch between environments/accounts without
re-entering credentials:

```bash
chek auth profile list
chek auth profile save dev-agent --activate
chek auth profile use dev-agent
chek auth profile export dev-agent --output ./dev-agent.profile.json
chek auth profile import dev-agent --file ./dev-agent.profile.json --activate
```

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

CI runs tests and `scripts/check_registry_drift.py --allow-missing-optional`.
Set `CHEK_BACKEND_SAAS_OPENAPI` to a backend-saas OpenAPI file or URL when it is
available; then the script compares the generated registry against the bundled
registry and fails on drift.

## Regenerate OpenAPI Registry

```bash
python scripts/generate_openapi_registry.py
```

The generator pulls dev gateway OpenAPI for `auth`, `backend-app`, `vehicle`,
`crowd`, and `humanoid`. If `backend-saas` is not exposed through the gateway,
export it from that repo with Java 17 and pass it explicitly:

```bash
JAVA_HOME=$(/usr/libexec/java_home -v 17) bash scripts/export_openapi.sh
python scripts/generate_openapi_registry.py \
  --source backend-saas=/path/to/backend-saas/build/swagger/backend-saas-openapi.json
```

## Dev Helpers

Frontend/browser commands are auxiliary, not the primary agent interface:

```bash
chek doctor
chek routes list
chek serve h5 --port 10086 --wait-seconds 60
chek flow smoke --url http://localhost:10086 --retries 10 --interval 2
```

Runtime pid/log files are written under `.agent-harness/run/` in the repository
root and are intentionally git-ignored.

## Release

Tag releases build wheel/sdist artifacts through GitHub Actions. If
`PYPI_API_TOKEN` is configured, tagged releases publish to PyPI. The repository
also includes a Dockerfile:

```bash
docker build -t chek-cli .
docker run --rm chek-cli manifest
```
