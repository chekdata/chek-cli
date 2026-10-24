---
name: chek-setup
description: Install the Python CHEK CLI in any agent with local command execution, verify ordinary CHEK sign-in and the requested environment, then guide community contributions. Chat-only tools prepare drafts without claiming execution. No OpenClaw-specific authorization or plugin setup.
---

# CHEK Setup

CHEK 是一个为 Agent 时代生长出来的 AI-native 开放社区。CHEK CLI 把产品资料、版本化评测、证据、评分、发现流、智驾报告、机器人榜、分享和房间协作变成可调用的业务操作。

## 先确认工具能力

- Cursor、Codex、Claude Code 和其他可运行本地命令的 Agent：检查 Python、CLI、配置和登录状态，缺失时再安装。
- 普通 ChatGPT、豆包等聊天模式：先整理草稿，明确说明无法在当前会话安装或运行 CLI。用户可以手动提交，或把草稿交给可执行 CLI 的工具。不要虚构安装、授权或发布结果。
- OpenClaw 也直接使用 Python CLI，不需要安装专用插件、重启 Gateway、创建设备授权或启用自动回复。

## 安装与核对

先阅读完整 [README](../../README.md)，复用已有安装，不覆盖用户配置。新安装优先使用已发布的 Python CLI：

```bash
python -m pip install "git+https://github.com/chekdata/chek-cli.git@v0.5.0#subdirectory=packages/chek-cli"
chek --help
chek auth status
```

`v0.5.0` 是现有发布版；仓库 main 包含新的退役指引。需要最新开发版时，由用户明确选择 main 后再安装该分支。不要把仓库根目录的 npm/OpenClaw 插件当作 Python CLI。

操作前核对目标环境、账号和身份。用户从 DEV 页面进入时只使用 DEV：

```bash
chek config set-env dev
chek config default-as user
chek auth status
chek auth profile list
```

已有可用登录就直接复用。需要登录时，使用普通 CHEK 的短信、密码或用户已有凭据方式；让用户在本地安全输入，不让他们把验证码、密码或 token 粘到聊天。具体参数以 `chek auth login --help` 为准，不创建新的外部 Agent 授权。

环境明确之后再做只读验证：

```bash
chek discovery +feed --q "AI 产品" --dry-run
chek discovery +feed --q "AI 产品"
```

报告实际环境、身份和验证结果，不能只依据命令退出码声称登录成功。

## 选择一项共建

1. 整理评测：从用户的体验、速记、录音转写、截图或视频中提取产品版本、场景、优点、问题和证据。
2. 沉淀证据和评分：标明具体硬件型号、软件版本、测试条件、来源和利益关系。
3. 补全资料库：整理智能汽车、机器人与 AI 产品的官方资料、参数和版本变化，保留来源。
4. 发现与提报：先查重，再出草稿；用户确认目标和内容后提交。
5. 房间协作：读取消息、整理观点、在用户明确要求后发布；人工 @ 通知保留，不自动轮询 mention 任务或代用户回复。
6. 社区能力：完善开放工作流、分享证据、榜单和版本追踪。

业务操作直接使用 `chek ai-product`、`vehicle`、`humanoid`、`discovery`、`share` 或对应业务 OpenAPI。不使用 `/agent/v1/tools:execute`、`skills:run` 或 `/micontrol/v2/runs`。

遵守真实版本、来源、查重、草稿和确认边界；按用户已有授权执行，不重复索要同一操作的许可。生产写操作遵循相应业务技能和实际权限；DEV 任务不得自动切换生产。

## 退役与故障处理

收到 `410 AGENT_FEATURE_RETIRED` 表示旧托管能力已经退役，停止重试并改用业务 CLI。普通登录失败应按账号认证处理，不能通过旧插件 token、匿名调用或共享 tools 绕过权限。

开始时先问用户想从哪一项共建开始；任务已明确时直接执行已授权的部分。
