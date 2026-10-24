# MeControl / hosted Agent retirement — DEV first

状态：实现完成，DEV 发布验证中（2026-10-24）。

新用户使用 Python CLI 和普通 CHEK 登录；不再推荐旧 OpenClaw 专用插件。旧插件收到 410 后停止轮询。

## 范围

整体退役目标：backend-micontrol-agent、backend-micontrol-runtime、backend-open-claw-adapter，以及站内自动 Agent 执行链。本次发布只进入 DEV。staging/prod 保持现有部署，不归档仓库，不删除数据库、对象存储或历史记录。

保留 CHEK CLI 业务能力、普通账号认证与权限、房间消息、人工 @ 提醒、未读、评测证据、评分、分享与 EGO 上传。外部 Agent 使用自己的执行环境调用普通业务接口。普通聊天工具先整理草稿，不宣称具备 CLI 执行能力。

## 发布顺序与回滚

1. 发布前端统一接入页，确认黑猫及 EGO 提示仍工作。
2. 发布 backend-app，验证旧接口 410、普通业务接口及房间通知。
3. GitOps 退役 DEV 三个独立工作负载及其 HPA/PDB/专用监控；保留退役标记防止自动重建。
4. 记录远端提交、运行镜像和实际资源状态。

需要回滚时先恢复 ops-bootstrap 退役前 DEV 配置并等三个服务就绪，再恢复 backend-app 和前端原镜像。新参与者默认提醒模式的迁移无历史数据删除。不要执行 cleanup_micontrol_data 等历史清理命令。

DEV 验证完成后才讨论其他环境迁移与仓库归档。
