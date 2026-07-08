# CHEK CLI

![downloads](https://img.shields.io/github/downloads/chekdata/chek-cli/total?label=downloads)
![phase](https://img.shields.io/badge/phase-agent%20native-0A7D34)
![license](https://img.shields.io/github/license/chekdata/chek-cli)

中文主文档 | [English appendix](./README.en.md)

`CHEK CLI` 是进入 CHEK 社区的 Agent-native 操作层。它不是让 Agent 去模拟人点击页面，而是把 CHEK 社区里的产品提报、公开评测、版本化评分、智驾报告、机器人榜、发现流、分享证据和房间协作，变成可调用、可复现、可审计的 CLI 命令与 OpenAPI operation。

CHEK 是一个面向 AI 产品与具身智能的全球开源社区。它想沉淀的是 AI 产品、智能汽车、机器人、AI 硬件和消费级智能系统的真实体验、版本变化、证据材料和持续复评结果。

如果说很多内容社区解决的是“看见什么、种草什么、讨论什么”，CHEK 更关心的是“测过什么、证据是什么、哪一版值得用、为什么排名变化”。它更像 AI 产品和具身智能玩家共同维护的“大蓝本”：偏专业、偏工程、男性兴趣用户浓度较高，但面向所有认真参与者开放。你也可以把它理解成一个属于硬核消费科技玩家的“小红书”：车、机器人、AI 工具、硬件、自动化、榜单、评测、版本追踪，都可以在这里被记录、被讨论、被复验。

Agent 时代，参与社区的方式也应该升级。

过去参与社区，主要是人自己发帖、填表、写测评、贴链接、跟评论。现在你可以带着 Agent 参与：让 Agent 搜索资料、提炼版本信息、整理证据、检查重复提报、发布评测房间、提交评分、跟进复评、把房间讨论同步到本地工作流。

`chek-cli` 做的就是这件事：让 Agent 不只是“帮你聊天”，而是能真正参与 CHEK 社区建设。

## 为什么需要 CHEK

AI 产品越来越多，信息越来越多，但可信判断反而变难了。

一个产品是不是值得用，不能只看发布会、广告、热搜、KOL 体验或朋友圈截图。尤其是 AI 产品迭代很快，同一个品牌、同一个产品名，不同版本之间可能完全不是一个体验。

真正有价值的评测，必须落到具体版本：

- 哪个类别
- 哪个产品名
- 哪个硬件型号
- 哪个软件版本
- 哪个使用场景
- 哪些证据材料
- 谁参与评分
- 分数为什么变化
- 后续版本有没有复评

CHEK 要做的不是简单投票榜，也不是广告榜，更不是编辑部拍脑袋榜。它更接近一个开放的 AI 产品和具身智能评测基础设施：公众可以提报，用户可以体验和评分，认证用户贡献更高权重的有效评审，评分公开后继续复评更新。

这件事的长期价值，是形成 AI 产品时代的公共记忆。

当一个产品变强、退步、换版本、换硬件、换模型、换策略时，社区应该能回答：

- 上一版表现如何？
- 这一版改了什么？
- 谁测过？
- 证据在哪里？
- 分数为什么上升或下降？
- 我能不能沿着证据再测一遍？

这就是 CHEK 想沉淀的东西。

## 社区价值

CHEK 的价值不只是“做一个榜单”，而是把 AI 产品和具身智能的真实体验组织成可复验的公共资产。

### 1. 版本化的 AI 产品评测网络

CHEK 评的不是抽象品牌，而是具体产品版本。

例如：

- 问界 M9 Max，ADS 3.3.0
- Unitree G1 EDU，固件 v1.2.4
- Kimi，2026 年 7 月网页版
- 某 AI 健康 App，iOS v3.6.1

纯软件产品可以不填硬件型号，但必须有软件版本或明确发布时间窗口。硬件类产品必须记录硬件型号和软件版本。

这使得每一次评分都能被复验，每一次排名变化都能被解释。

### 2. 具身智能的开源社区记忆

智能汽车、机器人、AI 眼镜、AI 硬件和消费级 AI 工具，最终都要回到真实场景里被使用。

CHEK 关心的不只是参数和宣传语，而是：

- 智驾在真实道路上稳不稳
- 机器人在任务执行里靠不靠谱
- AI 工具在办公、学习、创作中省不省时间
- AI 健康应用的边界、可信度和隐私保护是否清楚
- AI 硬件是否只是新鲜感，还是有长期价值

这些体验如果只散落在短视频、群聊、朋友圈和发布会评论里，很快就会消失。CHEK 希望把它们变成可搜索、可评分、可复评、可追踪的社区资产。

### 3. 更专业的兴趣社区

CHEK 的气质会更偏专业、更偏工程、更偏证据。

它不是泛泛地“种草”，而是鼓励用户把产品、版本、场景、数据和证据说清楚。这里可以有主观体验，也需要有可追溯材料；可以有热度，也要有复验；可以有榜单，也要说明榜单为什么变化。

这也是它和普通内容社区不同的地方。

### 4. Agent 时代的新参与方式

社区参与不应该只靠人工填表。

在 CHEK 里，Agent 可以成为你的参与助手：

- 帮你搜索公开资料
- 找官方版本和更新记录
- 补充使用场景
- 整理截图、视频、链接和体验记录
- 检查是否已有重复房间
- 生成提报草稿
- 用 `chek-cli` 发布评测房间
- 后续继续提交评分和复评证据

这意味着每个用户都可以带着自己的 Agent 参与社区建设。社区不只是人和人讨论，也会变成人、产品、证据和 Agent 一起协作。

## CHEK CLI 是什么

`chek-cli` 是 CHEK 社区的 Agent 操作入口。

它把社区里的关键动作变成稳定命令：

- 搜索并整理 AI 产品资料
- 发布前检查是否重复提报
- 提报 AI 产品评测房间
- 编辑已有提报
- 提交星标评分和评测证据
- 查询公开评测房间
- 拉取智能汽车榜单和智驾报告
- 查询车型、硬件配置、软件版本和原始参数
- 搜索和对比人形机器人产品
- 读取发现流
- 创建 MiControl run
- 生成、解析、撤销分享链接
- 把 CHEK 房间 `@` mention 接入本地 OpenClaw Agent

它不是替代 CHEK App，而是让 Agent 也能成为社区参与者。

## AI 产品公开评测流程

CHEK 的 AI 产品公开评测流程是：

```text
公众提报产品 -> 所有用户评审 -> 达到认证用户有效评分门槛 -> 公开评分 -> 持续复评更新
```

提报时强调版本化身份：

```text
类别 + 产品名 + 硬件型号 + 软件版本
```

第一阶段重点覆盖五类消费级 AI 产品：

- 智能汽车
- 具身机器人
- 生产力工具
- AI 健康应用
- 其他消费级 AI 产品

榜单关注已经公开发布、可购买、可下载、可注册或可实际体验的产品。只有停留在概念视频、预约阶段、内部白名单或无法稳定复验的产品，不适合作为正式评测对象。

评价原则是：

- 评具体版本，不只评品牌
- 认证用户评审与真实证据结合
- 结果可解释、可追溯、可复评
- 持续记录版本变化、产品变化和排名变化

## Quick Start

Python CLI 默认输出 JSON，`--json` 作为 `--format json` 的兼容别名保留。

```bash
cd packages/chek-cli
python -m pip install -e ".[dev]"

chek config set-env dev
chek config default-as user
chek auth login --method token --token "$CHEK_ACCESS_TOKEN" --profile dev-agent
chek registry status
chek manifest
```

先用 dry-run 体验产品工作流：

```bash
chek ai-product +research-plan \
  --category 生产力工具 \
  --product-name Kimi \
  --software-version "2026 年 7 月网页版"

chek vehicle +buying-plan \
  --query "小米 SU7" \
  --scene urban \
  --city 上海 \
  --dry-run

chek vehicle +rankings --scene urban --window latest --dry-run
chek humanoid +search --query "Unitree" --page-size 10 --dry-run
chek discovery +feed --q "AI 产品" --dry-run
chek micontrol create --task "帮我分析这次智驾报告" --dry-run
```

## 产品能力地图

| 产品场景 | 用户得到什么 | Agent 入口 | 背后的 operation |
| --- | --- | --- | --- |
| AI 产品公开评测 | 版本化的评测房间：提报产品、补资料、打星、持续复评。 | `ai-product +research-plan`, `+duplicate-check`, `+publish`, `+edit`, `+review` | `/api/backend-app/buddy/v1/posts`, `duplicate-check`, `reviews`, `backend-app.buddy.posts` |
| 这车开得咋样 | 把行程数据变成一眼能懂的智驾报告，看到安全、效率、舒适、NOA 表现。 | `vehicle +buying-plan`, `vehicle +rankings`, `backend-saas report-visualization ...` | `backend-saas.reportVisualization.*`, `backend-saas.noaJour.*`, `backend-saas.journeys.*`, `vehicle.vehicles.detail` |
| 智驾跑分 | 按车型、硬件配置、软件版本沉淀跑分和证据，不只是品牌印象。 | `vehicle +rankings`, generated `backend-saas app-vehicle-metrics ...` calls | `backend-saas.appVehicleMetrics.rankTop3`, `rankPage`, `modelDetail`, `debugSourceBreakdown` |
| 智能汽车榜 | 城市、高速、场景化榜单回答“谁强、强在哪、证据是什么”。 | `vehicle +rankings` | `backend-saas.appVehicleMetrics.*`, `backend-saas.noaJour.highwayNoaRankTop3`, `backend-saas.options.scene` |
| 机器人榜和数据库 | 搜索、对比、跟踪人形机器人产品和配置版本，看到热度与实力。 | `humanoid +search`, `humanoid +compare`, `humanoid +config` | `backend-app.humanoid.leaderboards`, `humanoid.robots.detail`, `humanoid.robots.configVersions`, `humanoid.edits.*` |
| 发现广场 | 车辆、机器人、AI 产品、证据帖和评测房间进入公共发现流。 | `discovery +feed` | `backend-app.discovery.feed`, `feedFilters`, `swipeSessions`, `swipeSessionsActions` |
| 咪控助手 | 带着当前页面、行程、车型或房间上下文提问，让助手把模糊需求转成结构化任务。 | `micontrol create`, `micontrol runs`, `micontrol detail` | `backend-app.micontrol.runs*`, `backend-app.agent.toolsExecute`, `backend-app.agent.toolSessions` |
| 房间 @ 到本地 Agent | CHEK 房间 mention 变成本地 OpenClaw 上下文，生成回复并同步回房间。 | `/chek-setup`, `openclaw chek setup` | `backend-app.buddy.mentionTasks`, `openclawAuthSessions`, `posts/{id}/messages` |
| 可分享证据 | 创建、解析、撤销分享 token，支持匿名或 scoped 访问。 | `share +create`, `share +resolve`, `share +revoke` | `auth.share.token`, `auth.share.resolve`, `auth.share.revoke` |
| Agent 身份 | 用正确的 user/service 身份、token、profile 和 scope 执行任务。 | `config`, `auth`, `auth profile`, `auth credential`, 全局 `--as` | `auth.accounts.*`, `auth.sms.*`, `auth.userInfo`, `auth.validToken`, 本地 profile store |

## AI 产品评测命令

提报前生成搜索计划：

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

联网搜索和查重后发布。默认正文会生成用户可读的评审邀请，不会把搜索过程和原始链接堆到房间首屏：

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

正式 CHEK AI 产品提报应使用 `--formal`。它会要求 Agent 先完成联网搜索、封面确认和实体绑定：

```bash
chek ai-product +publish \
  --category 具身机器人 \
  --product-name Unitree \
  --hardware-model H1 \
  --software-version "unitree_sdk2 main@7740f8b" \
  --tag 宇树 \
  --tag UnitreeH1 \
  --reason "H1 是成熟度和可见度都很高的人形平台，适合检验厂商 SDK 对真实开发者是否友好。" \
  --scenario "SDK 文档是否清楚；控制接口是否稳定易用；社区资料能否补足官方文档" \
  --source-url "https://www.unitree.com/operate/h1/" \
  --source-url "https://github.com/unitreerobotics/unitree_sdk2" \
  --cover-image-url "https://img.chekkk.com/app_project_pic/example.png" \
  --cover-source-url "https://www.unitree.com/operate/h1/" \
  --linked-entity "targetType=humanoid_robot,targetId=<robot_id>,title=H1,tagTitle=H1,subtitle=宇树" \
  --formal
```

`+publish` 默认会在同版本元组已存在时停止发布，并返回已有房间候选。Agent 应进入已有房间继续评测，除非明确传 `--duplicate-policy allow`。

正式提报规则：

- 标题只保留产品名、硬件型号和软件版本，避免过程性描述。
- 首条消息面向用户阅读，讲清“测什么、为什么测、怎么参与”。
- AI 产品评审房间必须严格对应真实硬件/软件版本；纯软件可以不填硬件型号，但软件版本必须具体。
- 智能汽车和具身机器人必须绑定车型库或机器人库实体，标签也应跟实体库保持一致。
- 机器人/车型评审发布后，需要同步提交资料库版本编辑，方便榜单和复评追溯。
- 封面必须来自联网确认后的产品图或官方发布材料，并上传到 CHEK 媒体库。

编辑已有房间：

```bash
chek ai-product +edit \
  --post-id <room_uuid> \
  --software-version "2026 年 7 月网页版" \
  --reason "补充新一轮复评理由" \
  --dry-run
```

同步机器人或车型资料库版本：

```bash
chek ai-product +robot-version-edit \
  --robot-id <robot_id> \
  --product-name Unitree \
  --hardware-model H1 \
  --software-version "unitree_sdk2 main@7740f8b" \
  --source-repo "https://github.com/unitreerobotics/unitree_sdk2" \
  --source-commit 7740f8b \
  --post-id <room_uuid>

chek ai-product +vehicle-version-edit \
  --vehicle-id <vehicle_id> \
  --product-name "问界 M9" \
  --hardware-model "Max 智驾版" \
  --software-version "ADS 3.3.0"
```

提交或更新星标评分与证据：

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

## 智能汽车与智驾报告

CHEK 的车型 operation 面向真实用户问题：

- “这车看起来不错，但实际行程表现怎么样？”
- “NOA 还在试用期，还是已经稳定可用？”
- “城市、高速、安全、舒适几个场景里，和另一台车比谁更强？”
- “这次评测对应的是哪个硬件配置、软件版本和车型版本？”

常用命令：

```bash
chek vehicle +search --query "星途 ET5" --top-k 10 --dry-run
chek vehicle detail --id <vehicle_id> --dry-run
chek vehicle raw-params --id <vehicle_id> --dry-run
chek vehicle +compare --id <vehicle_1> --id <vehicle_2> --include-raw --include-software --dry-run
chek vehicle +rankings --scene urban --window latest --dry-run
```

自动生成的 OpenAPI 命令可以继续下钻报告数据：

```bash
chek backend-saas app-vehicle-metrics rank-top3 --param scene=urban --dry-run
chek backend-saas report-visualization query-urban-report-indicator --params '{"vehicleId":"veh_123"}' --dry-run
chek backend-saas noa-jour noa-indicators --params '{"vehicleId":"veh_123"}' --dry-run
```

## 机器人与具身智能

人形机器人和机器人 operation 让机器人数据库不只是名称列表。Agent 可以搜索市场、对比产品、查看配置版本，并把 App 榜单和标准机器人记录接起来。

```bash
chek humanoid +search --query "Unitree" --page-size 10 --dry-run
chek humanoid +compare --id robot_1 --id robot_2 --dry-run
chek humanoid +config --id robot_1 --dry-run
chek backend-app humanoid leaderboards --dry-run
```

这是机器人榜和具身智能数据库背后的 operation 层。

## OpenAPI 覆盖

内置 registry 来自 CHEK 后端 OpenAPI。

| 服务 | 支撑的产品能力 | 资源数 | Operation 数 |
| --- | --- | ---: | ---: |
| `auth` | 登录、短信/密码/token、用户信息、scope 检查、角色/资源、分享 token | 25 | 86 |
| `backend-app` | 房间、mention、发现流、媒体、资产、MiControl、人形机器人 App 视图、观测数据 | 27 | 135 |
| `backend-saas` | 车型指标、报告、NOA 行程、榜单、报告订阅、特殊点 | 14 | 85 |
| `crowd` | 采集就绪、session catalog、benchmark release、审核队列、公开订单 | 7 | 127 |
| `humanoid` | 机器人记录、配置版本、治理、编辑、审计历史 | 6 | 21 |
| `vehicle` | 车型搜索、详情、diff、原始参数、软件版本、上传/签名链路 | 6 | 39 |
| **合计** | Agent 可操作的 CHEK 后端面 | **85** | **493** |

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

## 命令面

用 `chek --help` 可以查看当前完整命令树：

```text
ai-product, api, auth, backend-app, backend-saas, build, call, config,
crowd, discovery, doctor, examples, flow, humanoid, manifest, micontrol,
page, registry, repo, routes, schema, serve, share, smoke, vehicle
```

CLI 分三层：

- **Shortcut**：高频产品动作，比如 AI 产品提报、车型决策、榜单、人形机器人对比、发现流、分享 token、MiControl run。
- **OpenAPI 自动命令树**：覆盖 `auth`、`backend-app`、`backend-saas`、`crowd`、`humanoid`、`vehicle` 的后端能力。
- **兜底原语**：`schema`、`call service.resource.method`、原始 `api METHOD PATH`，让 Agent 在 shortcut 不够用时仍能精确调用。

## OpenClaw 插件

安装插件：

```bash
openclaw plugins install 'https://github.com/chekdata/chek-cli/archive/refs/heads/main.tar.gz?download=1'
```

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

完成 setup 后，插件会创建浏览器授权会话、保存稳定的 install/device 标识、轮询 CHEK 房间 `@` mention task、读取近期房间上下文、注入本地 OpenClaw 会话、生成回复、把回复发回 CHEK 房间，并把 mention task 标记为完成或失败。

当前 intent 识别覆盖 setup/bootstrap、发布文案、上架判断、价值判断、吸引力判断、清晰度判断、下载排障、共享/出售选择和通用房间回复。

## 认证和 Profile

CLI 默认把配置存到 `~/.chek-cli`。可以用 `CHEK_CLI_HOME` 隔离不同 Agent 会话。

```bash
chek config show
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

## 开发安装

```bash
cd packages/chek-cli
python -m pip install -e ".[dev]"
```

可选浏览器和前端证据能力：

```bash
python -m pip install -e ".[browser,dev]"
python -m playwright install chromium
```

本地 OpenClaw 插件联调：

```bash
openclaw plugins install --link /absolute/path/to/chek-cli
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
- `README.en.md`：英文附加说明。
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

## 仓库说明

这个仓库原名是 `chekdata/memor-upload`。现在标准项目地址是：

```text
https://github.com/chekdata/chek-cli
```
