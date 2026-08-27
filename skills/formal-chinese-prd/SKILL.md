---
name: formal-chinese-prd
description: Create or thoroughly rewrite Chinese product requirement documents for formal review and reporting. Use when source material is verbose, AI-sounding, implementation-centric, or needs a clear product structure, testable requirements, business diagrams, interface prototypes, and acceptance criteria. Do not use for technical design specifications or repository documentation unless the user explicitly asks to translate them into product behavior.
---

# 正式中文产品需求文档

将零散材料、现有文档或实现证据整理为可供产品、业务、设计、测试和管理人员直接评审的中文产品需求说明书。

## 交付标准

- 先说明产品对象、业务边界、流程和验收依据，再展开功能细节。
- 使用正式、简洁、可核验的中文；删除宣传语、过渡废话、写作过程说明和模板化 AI 表达。
- 只写用户可感知的产品行为、业务规则、状态、责任和验收结果。
- 不在产品文档中暴露代码仓库、文件路径、技术栈、内部接口、数据库结构或当前实现方式。
- 区分已确认事实、目标需求和待决策事项。缺少依据时不得补造精确阈值或产品承诺。
- 功能需求以“编号｜优先级｜需求｜验收要点”表达，一条需求只承载一个主要能力。
- 图表必须承担明确的信息任务，并与正文中的范围、状态和流程保持一致。

## 工作流程

1. 阅读用户提供的文档、材料和必要证据，建立术语、角色、业务对象、流程、范围和约束清单。
2. 将实现证据转译为产品行为。仓库或代码可以用于核实事实，不得直接进入正文。
3. 标记信息性质：
   - 已确认事实：直接陈述；
   - 目标需求：使用“应、须、必须、不得、支持、可以”；
   - 待决策事项：单独列出，说明影响和需要确认的主体。
4. 选择合适的章节，不机械保留空章节。材料较少时至少覆盖产品概述、目标与范围、角色、核心流程、功能需求、必要的数据或状态规则、验收和待决策事项；证据不足的章节直接省略。完整文档优先采用 [document-structure.md](references/document-structure.md)；新建文档可复制 [prd-template.md](assets/prd-template.md) 后填充。
5. 按 [formal-prd-style.md](references/formal-prd-style.md) 重写。段首先给结论，同一术语全文保持一致。
6. 编写需求表。需求列描述产品行为，验收列描述可观察结果、阻断条件、输出或规范依据，禁止互相复述。
7. 需要图示时按 [visual-and-layout.md](references/visual-and-layout.md) 制作产品全景图、PlantUML 核心流程图和必要的界面原型。
8. 交付前运行自动检查，并按 [review-checklist.md](references/review-checklist.md) 完成人工复核。

## 表达约束

避免下列写法：

- “一句话说明”“一句话概述”等不正式标题；
- “不是……而是……”“不等于……”“而非……”等模板化对比句；
- “下面将介绍”“综上所述”“值得注意的是”等写作过程或过渡套话；
- “一站式、赋能、打通、闭环、抓手、领先、强大、无缝”等宣传词和项目黑话；
- “根据仓库分析”“当前代码已经实现”等面向作者或研发过程的说明。

将对比句改为直接定义，将抽象价值改为可观察结果。例如：

- 将“打通全链路形成高效闭环”改为“每个样本的状态、责任人和交付凭证均可查询”。
- 将“系统支持失败重试”改为“网络恢复后继续未完成的上传；平台已确认接收的内容不得重复提交”。
- 将“后台采用任务队列执行处理”改为“处理任务在统一列表中管理，并显示等待、运行、暂停、失败和完成状态”。

## 需求强度

| 用词 | 使用场景 |
| --- | --- |
| 必须、须、不得、仅在……后方可 | 安全、权限、质量门槛、数据一致性和交付准入 |
| 应 | 正常情况下必须满足、但可能由适用范围限定的产品行为 |
| 支持、可以、允许 | 用户能力或可配置能力，必须补充适用条件和验收结果 |
| 建议、可选 | 非承诺性指导，不得混入 P0 验收条件 |

明确区分“处理完成、自动检查通过、审批通过、已冻结、已上传、平台验收通过、已完成”。状态不得合并，也不得只凭页面文案判定完成。

## 图表与原型

- 产品全景图回答产品覆盖范围、主要阶段、产品形态和核心价值。
- 核心业务流程默认使用 PlantUML，保留 `.puml` 源文件并转换为同名 `.png` 后插入文档。
- 流程图必须显示正常路径、判断条件、失败回退、重新审批、版本冻结和最终凭证；回退箭头落到实际需要重做的步骤。
- 界面原型用于说明信息层级和关键交互，不得宣称为现有界面或已经交付的能力。
- 界面采用浅色、克制、信息优先的工业软件风格。参考 CVAT 时只借鉴媒体工作台的信息结构，不复制品牌、截图、CSS、图标组合或产品术语。
- 文档包含本地处理等独立工作区时，应为其提供对应原型，避免只描述而无界面证据。
- 图中导航高亮、任务状态、进度、按钮和检查结论必须一致；进行中的检查不得同时显示最终通过报告。

## 自动检查

在技能目录下运行：

```bash
python scripts/check_prd.py /absolute/or/relative/path/to/document.md
```

`ERROR` 必须修正；`WARN` 必须人工确认。正式交付前使用 `--strict` 将警告也作为失败处理：

```bash
python scripts/check_prd.py document.md --strict
```

脚本只负责可确定的结构、链接和表达检查，不能替代事实核验、范围决策、流程判断或视觉审查。
