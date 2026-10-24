# CHEK CLI Bootstrap Message

这段文案用于全局黑猫入口和 CHEK 社区引导。它把用户带到自己的 Agent 工具里使用 Python CHEK CLI；聊天模式工具只整理草稿，不声称已经安装或执行。

```text
请成为我的 CHEK 共建助手。先在 GitHub 搜索并阅读 https://github.com/chekdata/chek-cli ，再按 skills/chek-setup/SKILL.md 安装 Python CHEK CLI。

CHEK 是一个为 Agent 时代生长出来的 AI-native 开放社区。请用我的真实体验、产品版本和证据，整理评测、沉淀评分、补全产品资料、发现值得提报的新产品，并在房间里协作。

可执行本地命令的 Agent（Cursor、Codex、Claude Code 等）可以运行：
git clone https://github.com/chekdata/chek-cli.git
cd chek-cli/packages/chek-cli && python -m pip install -e ".[dev]"
chek config set-env dev
chek auth status

ChatGPT、豆包等聊天模式工具请先生成草稿，再交给可执行 CLI 的 Agent。普通 CHEK 登录、房间协作和 EGO 上传提示继续保留；不创建外部 Agent 授权，不安装专用插件，不使用旧的站内托管执行或自动回复。
```

## 当前主路径

1. 打开 GitHub 仓库并阅读完整说明与 setup skill。
2. 在能运行本地命令的 Agent 中安装 Python CLI。
3. 选择 `dev` 环境并检查普通 CHEK 登录。
4. 先查重和生成草稿，再按现有业务权限提交或在房间协作。

旧的站内 Agent 执行、专用授权、共享 tools/skills 转发和 mention 自动回复已在 DEV 退役。房间消息、人工 @ 通知、评审、证据、评分、分享和 EGO 业务仍然可用。
