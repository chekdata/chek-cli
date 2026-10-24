# CHEK CLI Troubleshooting

## 新接入

在 Cursor、Codex、Claude Code 等可运行本地命令的 Agent 中执行：

```bash
git clone https://github.com/chekdata/chek-cli.git
cd chek-cli/packages/chek-cli
python -m pip install -e ".[dev]"
chek config set-env dev
chek auth status
```

普通 ChatGPT、豆包等聊天模式工具不能在当前会话安装或运行 CLI 时，应先输出草稿，并交给可执行 CLI 的 Agent。

## 旧插件仍显示状态

根目录 TypeScript 包只保留迁移兼容命令。`chek setup`、`chek-status` 和 `chek-bootstrap` 会指向 Python CLI，不创建授权会话、不轮询旧接口、不自动回复房间消息。旧配置中的授权字段会被忽略并清空，普通 CHEK 登录不受影响。

## 旧接口返回 410

这是预期退役信号。停止重试，改用 Python CLI 的业务命令，例如 `chek ai-product`、`chek vehicle`、`chek humanoid`、`chek discovery`、`chek share`，以及房间协作对应的业务 API。不要使用 `/agent/v1/tools:execute`、`skills:run` 或 `/micontrol/v2/runs`。

## 房间协作

房间消息、人工 @ 通知、评审、证据、评分和分享继续保留。mention 自动轮询和自动回复已移除；需要回复时由用户明确要求，并在自己的 Agent 中整理草稿后发布。
