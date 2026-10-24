# 旧授权流程已退役

DEV 已退役专用 Agent 授权、设备绑定和授权会话轮询。本文件只作为旧链接的迁移提示，不再提供浏览器授权、token 兜底或自动回复步骤。

新接入请阅读 [`skills/chek-setup/SKILL.md`](../skills/chek-setup/SKILL.md)，在自己的 Agent 工具中安装 Python CHEK CLI，并使用普通 CHEK 登录和业务权限。不要创建外部 Agent 授权，也不要重试旧授权接口；收到 `410 AGENT_FEATURE_RETIRED` 后应停止重试。
