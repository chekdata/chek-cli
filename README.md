# CHEK CLI

![downloads](https://img.shields.io/github/downloads/chekdata/chek-cli/total?label=downloads)
![phase](https://img.shields.io/badge/phase-agent%20native-0A7D34)
![license](https://img.shields.io/github/license/chekdata/chek-cli)

`CHEK CLI` is the agent-native command line surface for CHEK. It gives agents and developers a stable way to call CHEK backend capabilities, publish AI product review rooms, check duplicate submissions, submit ratings with evidence, and operate the OpenClaw helper that bridges CHEK room mentions into a local session.

The repository was formerly `chekdata/memor-upload`. The product focus is now CHEK CLI, and the canonical URL is:

```text
https://github.com/chekdata/chek-cli
```

For Chinese documentation, see [README.zh-CN.md](./README.zh-CN.md).

## What This Repository Ships

- `packages/chek-cli`: the Python agent-native CLI, installed as `chek` and `chek-cli`
- OpenAPI-backed command trees for CHEK backend services
- high-frequency shortcuts for vehicles, humanoid robots, discovery, share, MiControl, and AI product review rooms
- browser/token auth helpers with Lark-style `--as auto/user/service/none` identity switching
- an OpenClaw plugin helper for CHEK setup, room `@` mention sync, and auto-reply workflows
- setup skills and troubleshooting docs for agent installation

## AI Product Review Rooms

The new AI product workflow is built around version-specific review rooms:

```text
Public product submission -> all users review -> 5 valid Sun Chaser reviews -> public score -> continuous re-review
```

Agents can use the CLI to prepare richer submissions:

```bash
cd packages/chek-cli
python -m pip install -e ".[dev]"

chek ai-product +research-plan \
  --category 生产力工具 \
  --product-name Kimi \
  --software-version "2026 年 7 月网页版"
```

The research plan returns web-search queries, source expectations, and the duplicate-check payload. After the agent searches the web and collects sources, it can publish:

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

By default `+publish` runs duplicate-check first and stops when the same `category + product name + hardware model + software version` already exists. Use the matched room from the output to continue reviewing instead of creating a duplicate.

Submit a rating and evidence:

```bash
chek ai-product +review \
  --post-id <room_uuid> \
  --stars 4.5 \
  --comment "长文本总结稳定，版本已确认" \
  --evidence "附测试记录和截图链接" \
  --evidence-url "https://example.com/evidence"
```

Pure software products can leave `--hardware-model` empty, but `--software-version` is required because AI product rankings are version-specific.

## CHEK CLI

Local development:

```bash
cd packages/chek-cli
python -m pip install -e ".[dev]"
chek manifest
chek smoke api --dry-run
```

Core examples:

```bash
chek config show
chek config set-env dev
chek auth login --method token --token "$CHEK_ACCESS_TOKEN" --profile dev-agent
chek registry status
chek examples list

chek vehicle +buying-plan --query "小米 SU7" --scene urban --city 上海 --dry-run
chek humanoid +search --query "Unitree" --page-size 10 --dry-run
chek discovery +feed --q "AI 产品" --dry-run
chek api GET /api/backend-app/login/checkToken --dry-run
```

## OpenClaw Install

Current public install:

```bash
openclaw plugins install 'https://github.com/chekdata/chek-cli/archive/refs/heads/main.tar.gz?download=1'
```

Reserved npm package name:

```text
@chek/chek-cli
```

For local development:

```bash
openclaw plugins install --link /absolute/path/to/chek-cli
```

## Setup

In an OpenClaw chat:

```text
/chek-setup
```

From the CLI:

```bash
openclaw chek setup
```

If browser auth fails, fallback token setup still works:

```text
/chek-setup token=<CHEK_ACCESS_TOKEN>
```

```bash
openclaw chek setup --token <CHEK_ACCESS_TOKEN>
```

Useful follow-ups:

```text
/chek-status
/chek-bootstrap
```

```bash
openclaw chek status
openclaw chek bootstrap
```

## Bootstrap Message

```text
请在这台机器上安装并配置 CHEK CLI，并尽量自动完成初始化。

目标：
1. 安装 OpenClaw 插件 CHEK CLI
2. 安装后重启 Gateway
3. 自动拉起浏览器完成 CHEK 授权与设备绑定
4. 做一次连通性测试
5. 最后告诉我当前状态是否 ready

安装命令：
openclaw plugins install https://github.com/chekdata/chek-cli/archive/refs/heads/main.tar.gz?download=1

如果插件安装成功但不能自动继续，请立即执行 `/chek-setup`。插件会自动打开浏览器到 CHEK 授权页；浏览器显示“已授权，可返回 OpenClaw”后，回到本地继续等待健康检查完成。
如果浏览器授权失败，再退回 `/chek-setup token=<CHEK_ACCESS_TOKEN>` 或 `openclaw chek setup --token <CHEK_ACCESS_TOKEN>`。

参考链接：
- 插件说明：https://github.com/chekdata/chek-cli#readme
- setup skill：https://github.com/chekdata/chek-cli/blob/main/skills/chek-setup/SKILL.md
- 浏览器授权说明：https://github.com/chekdata/chek-cli/blob/main/docs/device-code-auth.md
- 排障说明：https://github.com/chekdata/chek-cli/blob/main/docs/troubleshooting.md
```

## Repository Layout

- `packages/chek-cli`: Python CHEK CLI package, installed as `chek` and `chek-cli`
- `src/index.ts`: OpenClaw plugin entry
- `src/service.ts`: background polling loop and task processor
- `src/commands.ts`: `/chek-setup`, `/chek-status`, `/chek-bootstrap`, and OpenClaw CLI commands
- `skills/chek-setup/SKILL.md`: bundled setup skill
- `docs/bootstrap-message.md`: user-facing bootstrap copy
- `docs/device-code-auth.md`: browser-auth flow and fallback rules
- `docs/troubleshooting.md`: common failure paths

## Development

```bash
pnpm install
pnpm build
pnpm test

cd packages/chek-cli
python -m pytest -q tests
```
