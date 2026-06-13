# CHEK CLI

![downloads](https://img.shields.io/github/downloads/chekdata/chek-cli/total?label=downloads)
![phase](https://img.shields.io/badge/phase-agent%20native-0A7D34)
![license](https://img.shields.io/github/license/chekdata/chek-cli)

`CHEK CLI` 是 CHEK 面向 Agent 和开发者的命令行入口。它把 CHEK 后端能力、AI 产品提报、版本化评测房间、发布前查重、评分与证据提交，以及 OpenClaw 房间助手能力，整理成稳定、可脚本化、适合 Agent 调用的 CLI。

这个仓库原名是 `chekdata/memor-upload`。现在项目名改为 `chek-cli`，标准地址是：

```text
https://github.com/chekdata/chek-cli
```

## 这个仓库现在包含什么

- `packages/chek-cli`：Python Agent-native CLI，安装后提供 `chek` 和 `chek-cli`
- CHEK 后端服务的 OpenAPI 自动命令树
- 智能汽车、具身机器人、发现流、分享、MiControl、AI 产品评测房间的高频 shortcut
- 浏览器授权 / token 授权，以及类似 Lark CLI 的 `--as auto/user/service/none` 身份切换
- OpenClaw 插件 helper：支持 CHEK setup、房间 `@` mention 同步和自动回复
- 面向 Agent 安装、授权、排障的 skill 与 docs

## AI 产品评测房间

新的 AI 产品流程是：

```text
公众提报产品 -> 所有用户评审 -> 达到 5 位追日靴有效评分 -> 公开评分 -> 持续复评更新
```

Agent 可以先用 CLI 生成提报前的联网搜索计划：

```bash
cd packages/chek-cli
python -m pip install -e ".[dev]"

chek ai-product +research-plan \
  --category 生产力工具 \
  --product-name Kimi \
  --software-version "2026 年 7 月网页版"
```

这个命令会返回：

- 建议搜索的关键词
- 应收集的资料类型
- 提交前查重所需的 payload
- 如果命中重复，应该进入已有房间继续评测的提示

Agent 完成联网搜索、补齐资料后，再发布：

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

`+publish` 默认会先调用查重接口。如果相同的 `类别 + 产品名 + 硬件型号 + 软件版本` 已经存在，CLI 会停止发布，并把已有房间候选返回给 Agent；除非明确使用 `--duplicate-policy allow`。

提交评分与评测证据：

```bash
chek ai-product +review \
  --post-id <room_uuid> \
  --stars 4.5 \
  --comment "长文本总结稳定，版本已确认" \
  --evidence "附测试记录和截图链接" \
  --evidence-url "https://example.com/evidence"
```

纯软件产品可以不填 `--hardware-model`，但 `--software-version` 必填，因为 AI 产品评分必须锚定到某个具体版本。

## CHEK CLI 常用命令

本地开发：

```bash
cd packages/chek-cli
python -m pip install -e ".[dev]"
chek manifest
chek smoke api --dry-run
```

常用示例：

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

## OpenClaw 安装

当前公开可用的安装方式：

```bash
openclaw plugins install 'https://github.com/chekdata/chek-cli/archive/refs/heads/main.tar.gz?download=1'
```

预留 npm 包名：

```text
@chek/chek-cli
```

本地开发联调：

```bash
openclaw plugins install --link /absolute/path/to/chek-cli
```

## 配置

在 OpenClaw 对话里执行：

```text
/chek-setup
```

在命令行里执行：

```bash
openclaw chek setup
```

浏览器授权失败时的兜底方式：

```text
/chek-setup token=<CHEK_ACCESS_TOKEN>
```

```bash
openclaw chek setup --token <CHEK_ACCESS_TOKEN>
```

辅助命令：

```text
/chek-status
/chek-bootstrap
```

```bash
openclaw chek status
openclaw chek bootstrap
```

## 一段式 bootstrap message

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

## 仓库结构

- `packages/chek-cli`：Python CHEK CLI 包，安装后提供 `chek` 和 `chek-cli`
- `src/index.ts`：OpenClaw 插件入口
- `src/service.ts`：后台轮询和 task 处理
- `src/commands.ts`：`/chek-setup`、`/chek-status`、`/chek-bootstrap` 和 OpenClaw CLI 命令
- `skills/chek-setup/SKILL.md`：随插件一起发的 setup skill
- `docs/bootstrap-message.md`：面向用户的一段式引导文案
- `docs/device-code-auth.md`：浏览器授权链路和 fallback 规则
- `docs/troubleshooting.md`：排障说明

## 开发

```bash
pnpm install
pnpm build
pnpm test

cd packages/chek-cli
python -m pytest -q tests
```
