# CHEK CLI

![downloads](https://img.shields.io/github/downloads/chekdata/chek-cli/total?label=downloads)
![phase](https://img.shields.io/badge/phase-agent%20native-0A7D34)
![license](https://img.shields.io/github/license/chekdata/chek-cli)

`CHEK CLI` 是 CHEK 面向 Agent 的命令行和 OpenClaw 插件入口。它把 CHEK 后端能力、版本化 AI 产品评测房间、OpenAPI 自动命令树、认证 profile、以及 CHEK 房间 `@` mention 到本地 OpenClaw 会话的桥接能力，整理成稳定、可脚本化、适合 Agent 调用的工具。

这个仓库原名是 `chekdata/memor-upload`。现在标准项目地址是：

```text
https://github.com/chekdata/chek-cli
```

English documentation: [README.md](./README.md).

## 这个仓库包含什么

- `packages/chek-cli`：Python Agent-native CLI，安装后提供 `chek` 和 `chek-cli`。
- CHEK 后端 6 个服务、493 个 operation 的 OpenAPI 自动命令树。
- AI 产品评测房间、智能汽车、人形机器人、发现流、分享链接、MiControl run 的稳定 shortcut。
- 类 Lark 的认证和 profile 管理：`--as auto/user/service/none`、浏览器/token/短信/密码登录、命名 profile、scope credential、`CHEK_CLI_HOME` 会话隔离。
- OpenClaw 插件 helper：`/chek-setup`、`/chek-status`、`/chek-bootstrap`、浏览器授权、CHEK 房间 mention 轮询、本地上下文注入、房间自动回复。
- 随仓库发布的 CHEK setup skill 和 AI 产品候选库 sourcing skill。
- 用于本地 App 诊断的前端、构建、浏览器证据辅助命令。

## 安装

本地安装 Python CLI：

```bash
cd packages/chek-cli
python -m pip install -e ".[dev]"
```

可选浏览器和前端证据能力：

```bash
python -m pip install -e ".[browser,dev]"
python -m playwright install chromium
```

安装 OpenClaw 插件：

```bash
openclaw plugins install 'https://github.com/chekdata/chek-cli/archive/refs/heads/main.tar.gz?download=1'
```

本地 OpenClaw 插件联调：

```bash
openclaw plugins install --link /absolute/path/to/chek-cli
```

## 快速开始

Python CLI 默认输出 JSON，`--json` 作为 `--format json` 的兼容别名保留。

```bash
chek config show
chek config set-env dev
chek config default-as user
chek auth status
chek auth login --method token --token "$CHEK_ACCESS_TOKEN" --profile dev-agent
chek registry status
chek manifest
```

面向 Agent 的常用例子：

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

## 命令面

用 `chek --help` 可以查看当前完整命令树。顶层命令包括：

```text
ai-product, api, auth, backend-app, backend-saas, build, call, config,
crowd, discovery, doctor, examples, flow, humanoid, manifest, micontrol,
page, registry, repo, routes, schema, serve, share, smoke, vehicle
```

| 层级 | 命令 | 用途 |
| --- | --- | --- |
| AI 产品房间 | `ai-product +research-plan`, `+duplicate-check`, `+publish`, `+edit`, `+review`, `+list`, `+detail` | 候选资料准备、发布前查重、房间发布/编辑、评分、证据提交和房间查询 |
| 智能汽车 shortcut | `vehicle +search`, `detail`, `raw-params`, `+buying-plan`, `+compare`, `+rankings` | 车型搜索、详情、原始参数、购车计划、车型对比和榜单查看 |
| 人形机器人 shortcut | `humanoid +search`, `+compare`, `+config` | 人形机器人数据库搜索、对比、配置版本查询 |
| 其他 shortcut | `discovery +feed`, `share +create/+resolve/+revoke`, `micontrol runs/detail/create` | 发现流、分享 token、MiControl run 编排 |
| OpenAPI 自动命令树 | `auth`、`backend-app`、`backend-saas`、`crowd`、`humanoid`、`vehicle` 下的资源/方法命令 | 基于内置 registry 的后端能力覆盖 |
| API 兜底 | `schema`, `call`, `api` | schema 发现、按 registry 调方法、原始 `METHOD PATH` 后端调用 |
| 会话和认证 | `config`, `auth`, `auth profile`, `auth credential`, 全局 `--as` | 环境/origin 配置、身份切换、登录、profile 导入导出、scope credential 检查 |
| 证据和调试辅助 | `doctor`, `repo`, `routes`, `serve`, `build`, `page`, `flow`, `smoke`, `examples`, `manifest` | 仓库诊断、H5 服务、路由/页面证据、smoke、例子和 Agent manifest |

## OpenAPI 覆盖

内置 registry 来自 CHEK 后端 OpenAPI。

| 服务 | 资源数 | Operation 数 |
| --- | ---: | ---: |
| `auth` | 25 | 86 |
| `backend-app` | 27 | 135 |
| `backend-saas` | 14 | 85 |
| `crowd` | 7 | 127 |
| `humanoid` | 6 | 21 |
| `vehicle` | 6 | 39 |
| **合计** | **85** | **493** |

常用 registry 和原始调用命令：

```bash
chek registry status
chek schema vehicle.vehicles.batchSearch
chek call vehicle.vehicles.detail --path id=veh_123 --dry-run
chek vehicle vehicles batch-search \
  --data '{"queries":[{"query":"小米 SU7"}]}' \
  --dry-run
chek api GET /api/backend-app/login/checkToken --dry-run
```

## AI 产品评测房间

AI 产品流程是版本化的：

```text
公众提报产品 -> 所有用户评审 -> 达到 5 位追日靴有效评分 -> 公开评分 -> 持续复评更新
```

查重身份元组是：

```text
类别 + 产品名 + 硬件型号 + 软件版本
```

纯软件产品可以不填 `--hardware-model`，但 `--software-version` 必填，因为评分和榜单必须锚定到某个具体版本。

提报前先生成搜索计划：

```bash
chek ai-product +research-plan \
  --category 生产力工具 \
  --product-name Kimi \
  --software-version "2026 年 7 月网页版"
```

发布前查重：

```bash
chek ai-product +duplicate-check \
  --category 具身机器人 \
  --product-name "Unitree G1" \
  --hardware-model EDU \
  --software-version v1.2.4 \
  --dry-run
```

联网搜索和查重后发布：

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

`+publish` 默认会在同版本元组已存在时停止发布，并返回已有房间候选。Agent 应进入已有房间继续评测，除非明确传 `--duplicate-policy allow`。

编辑已有房间：

```bash
chek ai-product +edit \
  --post-id <room_uuid> \
  --software-version "2026 年 7 月网页版" \
  --reason "补充新一轮复评理由" \
  --dry-run
```

提交或更新评分与证据：

```bash
chek ai-product +review \
  --post-id <room_uuid> \
  --stars 4.5 \
  --comment "长文本总结稳定，版本已确认" \
  --evidence "附测试记录和截图链接" \
  --evidence-url "https://example.com/evidence"
```

查看房间：

```bash
chek ai-product +list --scope public --dry-run
chek ai-product +detail --post-id <room_uuid> --dry-run
```

## 认证和 Profile

CLI 默认把配置存到 `~/.chek-cli`。可以用 `CHEK_CLI_HOME` 隔离不同 Agent 会话。

```bash
chek config set-env dev
chek config set-origin https://api-dev.chekkk.com/api/backend-app
chek config default-as user
chek config secret-store keyring
```

支持的登录和凭证辅助：

```bash
chek auth login --method token --token "$CHEK_ACCESS_TOKEN" --profile dev-agent
chek auth sms-send --phone "13800000000"
chek auth login --method sms --phone "13800000000" --code "123456" --profile dev-agent
chek auth login --method password --phone "13800000000" --password "$CHEK_PASSWORD"
chek auth credential set --profile dev-agent --identity service --token "$CHEK_SERVICE_TOKEN"
chek --as service auth status
chek auth check --scope vehicle:read --verify
```

命名 profile 让 Agent 可以在不同环境或账号之间切换：

```bash
chek auth profile list
chek auth profile save dev-agent --activate
chek auth profile use dev-agent
chek auth profile export dev-agent --output ./dev-agent.profile.json
chek auth profile import dev-agent --file ./dev-agent.profile.json --activate
```

## OpenClaw 插件

OpenClaw 对话命令：

```text
/chek-setup
/chek-status
/chek-bootstrap
```

CLI 等价命令：

```bash
openclaw chek setup
openclaw chek status
openclaw chek bootstrap
```

默认 setup 走浏览器授权。浏览器授权失败时，token 兜底仍然可用：

```text
/chek-setup token=<CHEK_ACCESS_TOKEN>
```

```bash
openclaw chek setup --token <CHEK_ACCESS_TOKEN>
```

完成 setup 后，插件可以：

- 创建并轮询 CHEK 浏览器授权会话。
- 保存稳定的 install/device 标识。
- 轮询 CHEK 房间里的 `@` mention task。
- 读取近期房间上下文，并注入到稳定的本地 OpenClaw 会话。
- 通过直接 intent 规则、本地会话 prompt 或 fallback 文案生成回复。
- 把回复发回 CHEK 房间，并把 mention task 标记为完成或失败。

当前 intent 识别覆盖 setup/bootstrap、发布文案、上架判断、价值判断、吸引力判断、清晰度判断、下载排障、共享/出售选择和通用房间回复。

## 内置 Skills

- [`skills/chek-setup/SKILL.md`](./skills/chek-setup/SKILL.md)：帮助 OpenClaw 完成 CHEK CLI setup、浏览器授权、token 兜底和健康检查。
- [`skills/chek-ai-product-sourcing/SKILL.md`](./skills/chek-ai-product-sourcing/SKILL.md)：帮助 Agent 搜索、验证、分类、去重和整理 CHEK AI 产品候选，再进入正式 CLI 提报阶段。它只写本地文件或用户本轮指定的飞书/Lark 候选库，不硬编码默认候选库。

## 前端和证据辅助

这些命令只是辅助能力。当需要本地 App 视觉证据、路由证据、构建证据或 smoke-flow 证据时使用。

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

运行时 pid/log 会写到仓库 `.agent-harness/run/`，默认不提交。

## Examples 和 Smoke

```bash
chek examples list
chek examples show vehicle.buying-plan
chek examples generate --service vehicle --resource vehicles --limit 5
chek manifest --include-operations --operation-limit 20
chek smoke api --dry-run
chek smoke auth --dry-run
chek smoke api --include-authenticated --include-auth-check
```

## 重新生成 OpenAPI Registry

```bash
cd packages/chek-cli
python scripts/generate_openapi_registry.py
```

生成器会从 dev 网关拉取 `auth`、`backend-app`、`vehicle`、`crowd`、`humanoid` 的 OpenAPI。如果 `backend-saas` 没有通过网关暴露，需要在 `backend-saas` 仓库用 Java 17 先导出：

```bash
JAVA_HOME=$(/usr/libexec/java_home -v 17) bash scripts/export_openapi.sh
python scripts/generate_openapi_registry.py \
  --source backend-saas=/path/to/backend-saas/build/swagger/backend-saas-openapi.json
```

CI 也会运行 `scripts/check_registry_drift.py --allow-missing-optional`。如果能提供 backend-saas OpenAPI 文件或 URL，可以设置 `CHEK_BACKEND_SAAS_OPENAPI`。

## 仓库结构

- `packages/chek-cli`：Python CHEK CLI 包和生成的 OpenAPI registry。
- `packages/chek-cli/README.md`：package 级 CLI 说明。
- `src/index.ts`：OpenClaw 插件入口。
- `src/commands.ts`：`/chek-setup`、`/chek-status`、`/chek-bootstrap` 和 OpenClaw CLI 命令。
- `src/service.ts`：后台轮询、浏览器授权同步、mention task 处理、房间回复编排。
- `src/render.ts`：房间上下文压缩、intent 识别、直接回复和本地 prompt 构造。
- `skills/chek-setup/SKILL.md`：随仓库发布的 setup skill。
- `skills/chek-ai-product-sourcing/SKILL.md`：随仓库发布的 AI 产品候选 sourcing skill。
- `docs/bootstrap-message.md`：面向用户的一段式引导文案。
- `docs/device-code-auth.md`：浏览器授权链路和 fallback 规则。
- `docs/troubleshooting.md`：常见排障路径。

## 开发

```bash
pnpm install
pnpm build
pnpm test

cd packages/chek-cli
python -m pip install -e ".[dev]"
python -m pytest -q tests
```

## 发布

打 tag 会通过 GitHub Actions 构建 wheel/sdist。如果配置了 `PYPI_API_TOKEN`，tag release 会自动发布到 PyPI。仓库也提供 Dockerfile：

```bash
docker build -t chek-cli .
docker run --rm chek-cli manifest
```
