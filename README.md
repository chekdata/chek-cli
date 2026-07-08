# CHEK CLI

![downloads](https://img.shields.io/github/downloads/chekdata/chek-cli/total?label=downloads)
![phase](https://img.shields.io/badge/phase-agent%20native-0A7D34)
![license](https://img.shields.io/github/license/chekdata/chek-cli)

`CHEK CLI` is the agent-native command line and OpenClaw plugin surface for CHEK. It gives agents and developers a stable way to call CHEK backend capabilities, publish and review version-specific AI product rooms, operate generated OpenAPI command trees, manage auth profiles, and bridge CHEK room `@` mentions into a local OpenClaw session.

This repository was formerly `chekdata/memor-upload`. The canonical project is now:

```text
https://github.com/chekdata/chek-cli
```

Chinese documentation: [README.zh-CN.md](./README.zh-CN.md).

## What This Repository Ships

- `packages/chek-cli`: the Python agent-native CLI, installed as `chek` and `chek-cli`.
- OpenAPI-backed command trees for 6 CHEK backend services and 493 operations.
- Stable shortcuts for AI product review rooms, vehicles, humanoid robots, discovery feeds, share links, and MiControl runs.
- Lark-style auth/profile management with `--as auto/user/service/none`, browser/token/SMS/password login helpers, named profiles, scoped credentials, and `CHEK_CLI_HOME` session isolation.
- An OpenClaw plugin helper for `/chek-setup`, `/chek-status`, `/chek-bootstrap`, browser authorization, CHEK room mention polling, local context injection, and room auto-replies.
- Bundled skills for CHEK setup and AI product candidate sourcing.
- Optional frontend/build/browser evidence helpers for local app diagnostics.

## Install

Install the Python CLI for local development:

```bash
cd packages/chek-cli
python -m pip install -e ".[dev]"
```

Optional browser and frontend evidence helpers:

```bash
python -m pip install -e ".[browser,dev]"
python -m playwright install chromium
```

Install the OpenClaw plugin:

```bash
openclaw plugins install 'https://github.com/chekdata/chek-cli/archive/refs/heads/main.tar.gz?download=1'
```

For local OpenClaw plugin development:

```bash
openclaw plugins install --link /absolute/path/to/chek-cli
```

## Quick Start

The Python CLI emits JSON by default. `--json` is kept as a compatibility alias for `--format json`.

```bash
chek config show
chek config set-env dev
chek config default-as user
chek auth status
chek auth login --method token --token "$CHEK_ACCESS_TOKEN" --profile dev-agent
chek registry status
chek manifest
```

Agent-oriented examples:

```bash
chek ai-product +research-plan \
  --category 生产力工具 \
  --product-name Kimi \
  --software-version "2026 年 7 月网页版"

chek vehicle +buying-plan --query "小米 SU7" --scene urban --city 上海 --dry-run
chek humanoid +search --query "Unitree" --page-size 10 --dry-run
chek discovery +feed --q "AI 产品" --dry-run
chek api GET /api/backend-app/login/checkToken --dry-run
```

## Command Surface

Run `chek --help` to inspect the current command tree. The top-level CLI includes:

```text
ai-product, api, auth, backend-app, backend-saas, build, call, config,
crowd, discovery, doctor, examples, flow, humanoid, manifest, micontrol,
page, registry, repo, routes, schema, serve, share, smoke, vehicle
```

| Layer | Commands | Purpose |
| --- | --- | --- |
| AI product rooms | `ai-product +research-plan`, `+duplicate-check`, `+publish`, `+edit`, `+review`, `+list`, `+detail` | Product sourcing, duplicate checks, room publishing/editing, rating, evidence submission, and room lookup |
| Vehicle shortcuts | `vehicle +search`, `detail`, `raw-params`, `+buying-plan`, `+compare`, `+rankings` | Intelligent vehicle search, detail, raw params, purchase planning, comparison, and ranking inspection |
| Humanoid shortcuts | `humanoid +search`, `+compare`, `+config` | Humanoid robot database search, comparison, and configuration-version lookup |
| Other shortcuts | `discovery +feed`, `share +create/+resolve/+revoke`, `micontrol runs/detail/create` | Discovery feed, share-token operations, and MiControl run orchestration |
| Generated OpenAPI tree | `auth`, `backend-app`, `backend-saas`, `crowd`, `humanoid`, `vehicle` resource/method commands | Broad generated backend coverage based on the bundled registry |
| API fallback | `schema`, `call`, `api` | Schema discovery, registry-backed method calls, and raw `METHOD PATH` backend calls |
| Session and auth | `config`, `auth`, `auth profile`, `auth credential`, global `--as` | Environment/origin config, identity switching, login, profile import/export, and scoped credential checks |
| Evidence/dev helpers | `doctor`, `repo`, `routes`, `serve`, `build`, `page`, `flow`, `smoke`, `examples`, `manifest` | Repo diagnostics, H5 server lifecycle, route/page evidence, smoke tests, examples, and agent manifests |

## OpenAPI Coverage

The bundled registry is generated from CHEK backend OpenAPI specs.

| Service | Resources | Operations |
| --- | ---: | ---: |
| `auth` | 25 | 86 |
| `backend-app` | 27 | 135 |
| `backend-saas` | 14 | 85 |
| `crowd` | 7 | 127 |
| `humanoid` | 6 | 21 |
| `vehicle` | 6 | 39 |
| **Total** | **85** | **493** |

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

## AI Product Review Rooms

The AI product workflow is version-specific:

```text
Public product submission -> all users review -> 5 valid Sun Chaser reviews -> public score -> continuous re-review
```

The identity tuple for duplicate checks is:

```text
category + product name + hardware model + software version
```

Pure software products can leave `--hardware-model` empty, but `--software-version` is required because rankings and reviews must point to a specific version.

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

`+publish` stops by default when the same version tuple already exists. Use the matched room from the output to continue reviewing instead of creating a duplicate, or explicitly pass `--duplicate-policy allow`.

Edit an existing room:

```bash
chek ai-product +edit \
  --post-id <room_uuid> \
  --software-version "2026 年 7 月网页版" \
  --reason "补充新一轮复评理由" \
  --dry-run
```

Submit or update a rating with evidence:

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

## Auth And Profiles

The CLI stores config under `~/.chek-cli` by default. Set `CHEK_CLI_HOME` to isolate an agent session.

```bash
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

## OpenClaw Plugin

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

After setup, the plugin can:

- create and poll CHEK browser-auth sessions.
- persist stable install and device identifiers.
- poll CHEK room `@` mention tasks.
- load recent room context and inject it into a stable local OpenClaw session.
- generate local replies using direct intent rules, local session prompting, or fallback reply text.
- send the reply back to the CHEK room and complete or fail the mention task.

Intent handling currently covers setup/bootstrap, posting copy, listing readiness, value judgement, appeal judgement, clarity judgement, download troubleshooting, distribution choice, and generic room replies.

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
