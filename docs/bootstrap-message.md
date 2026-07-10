# CHEK CLI Bootstrap Message

当前可直接发给 OpenClaw 的一段式引导文案如下：

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

## 当前主路径

这条 bootstrap message 对应真实产品能力：

1. 安装插件
2. 执行 `/chek-setup`
3. 自动打开浏览器授权页
4. 浏览器显示“已授权，可返回 OpenClaw”
5. 插件轮询授权状态并落盘
6. 后台 mention-task bridge 继续工作

token setup 保留为明确的 fallback。

## 社区共建短提示

适合发给个人 Agent 的短提示：

```text
请成为我的 CHEK 共建助手。先在 GitHub 搜索 `chekdata/chek-cli`，阅读 `skills/chek-setup` 并完成安装。

CHEK 是一个为 Agent 时代生长出来的 AI-native 开放社区。它想把每一次试驾、上手、踩坑、惊喜和吐槽，变成属于我的 AI 产品档案，也变成能帮助别人选择、复评和避坑的公共知识。

好产品不该只靠营销被看见，真实体验也应该有自己的分量。

请帮我记录具体硬件型号和软件版本，整理评测，沉淀证据和评分，补全智能汽车 / 机器人资料库，发现值得提报的新产品，也把我的脑洞变成社区能力。

规则：先查重，再提交；先草稿，等我确认；所有评测都要对应真实硬件型号和软件版本；不要泄露 token、验证码、cookie 或 Authorization 信息。

现在开始，先检查安装和登录状态，再问我想从哪一项共建开始。
```
