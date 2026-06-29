# Agent Factory 需求文档

## 1. 项目定位

Agent Factory 是一个用于构建、运行、管理和迭代个人常驻智能体的工作台。它的目标不是简单创建聊天机器人，而是把“我想要一个什么样的 agent”转化为一组可运行、可调度、可观测、可更新的 agent 实例。

系统需要支持用户定义 agent 的角色、目标、状态、动作、工具、任务、权限、记忆和协作关系，并将这些定义编译为可执行的工作流。最终形成一个能够长期常驻、自主观察、主动执行、沉淀经验、持续增强的个人 agent 系统。

## 2. 核心目标

Agent Factory 的核心目标包括：

1. 允许用户通过可视化页面定义 agent 的组成，而不是手写大量 prompt 或代码。
2. 支持将 agent 需求转化为标准化 Agent Spec。
3. 支持基于 Agent Spec 生成可执行 agent、任务流、工具权限和记忆配置。
4. 支持多个 agent 常驻运行，并围绕任务进行协作。
5. 支持 agent 定期从网络、文件、代码仓库、知识库等来源获取信息。
6. 支持知识库、经验库、技能库的构建、更新和审查。
7. 支持任务视图、agent 视图、工具视图、记忆视图、审批视图和运行日志视图。
8. 支持低人工干预运行，但对高风险动作保留人工确认。
9. 支持后续接入 OpenClaw、Agent Zero、LangGraph、Claude Code、n8n、Dify、Letta 等外部系统作为组件。

## 3. 非目标

第一阶段不追求以下能力：

1. 不做通用商业化 agent 平台。
2. 不追求多用户权限体系。
3. 不追求复杂企业级工作流审批。
4. 不要求 agent 完全自主修改自身核心代码。
5. 不要求兼容所有 agent 框架。
6. 不要求一开始支持复杂多模态操作。
7. 不要求完全替代 Dify、OpenClaw、Agent Zero、n8n 等现有工具。

第一阶段重点是：建立 agent 的标准化定义、任务运行闭环和个人可用的管理界面。

## 4. 用户场景

### 4.1 Research Agent

用户希望创建一个 Research Agent，使其能够定期监控论文、会议、GitHub 项目、技术博客和新闻，并判断哪些信息与当前研究项目相关。

典型流程：

1. 用户在 Agent Factory 中创建 Research Agent。
2. 设置关注主题，例如 ECG audit、medical AI safety、patient trajectory modeling。
3. 设置数据源，例如 arXiv、Google Scholar、GitHub、RSS、特定网页。
4. 设置运行频率，例如每天早上 8 点。
5. agent 定期搜索、去重、摘要、打分。
6. agent 将结果分为：忽略、临时记录、进入知识库、进入经验库、创建任务。
7. 高价值发现进入用户日报或审批队列。

### 4.2 Project Manager Agent

用户希望创建一个 Project Manager Agent，使其能够维护项目进度、拆解任务、识别阻塞并提出下一步行动建议。

典型流程：

1. 用户录入项目列表。
2. agent 定期读取任务状态、GitHub 变更、文件修改、研究发现。
3. agent 生成项目状态报告。
4. agent 对 overdue、blocked、waiting decision 的任务进行标记。
5. agent 必要时提出开会、写邮件、分配任务或创建子任务建议。
6. 涉及外部动作时进入审批队列。

### 4.3 Memory Curator Agent

用户希望有一个 Memory Curator Agent，负责判断哪些内容应该进入知识库、经验库或技能库。

典型流程：

1. Research Agent 或 Project Manager Agent 产生候选记忆。
2. Memory Curator Agent 判断内容类型。
3. 对事实性资料写入知识库。
4. 对任务经验写入经验库。
5. 对可复用流程写入技能库。
6. 对不确定内容标记为 pending_review。
7. 对过时或冲突内容提出更新建议。

### 4.4 Code Worker Agent

用户希望某些 agent 可以调用 Claude Code 或其他 coding agent 完成代码任务。

典型流程：

1. Project Manager Agent 创建代码任务。
2. Code Worker Agent 读取任务说明。
3. 系统为其分配工作目录和权限。
4. Code Worker Agent 生成代码、脚本或文档。
5. Evaluator Agent 检查输出。
6. 修改核心仓库、提交 PR 或删除文件时必须人工确认。

## 5. 核心概念模型

### 5.1 Agent

Agent 是系统中的长期运行实体，具有明确角色、目标、状态、工具、任务和记忆。

Agent 的基本结构：

```yaml
agent_id: research_agent_ecg
name: ECG Research Agent
role: Research Agent
mission: Monitor ECG and medical AI research related to evidence audit.
status: active
autonomy_level: L2
triggers:
  - type: schedule
    cron: "0 8 * * *"
tools:
  - web_search
  - browser
  - vector_db
  - task_db
memory_access:
  read:
    - knowledge_base
    - experience_base
    - project_context
  write:
    - candidate_memory
actions:
  auto:
    - search_sources
    - summarize
    - score_relevance
    - create_candidate_memory
  approval_required:
    - send_email
    - create_calendar_event
    - modify_skill
evaluation:
  - source_required
  - relevance_score_required
  - duplication_check
```

### 5.2 Task

Task 是 agent 执行工作的基本单位。

Task 的基本结构：

```yaml
task_id: task_20260629_001
title: Search new ECG perturbation audit papers
type: research_scan
owner_agent: research_agent_ecg
project_id: ecg_audit
status: running
priority: high
created_by: schedule
input:
  topics:
    - ECG explainability
    - perturbation audit
    - attribution reliability
expected_output:
  - paper_candidates
  - relevance_scores
  - action_suggestions
requires_approval: false
```

Task 状态包括：

```text
created
queued
running
waiting_approval
blocked
completed
failed
cancelled
```

### 5.3 Tool

Tool 是 agent 可以调用的外部能力。

工具类型包括：

1. 信息获取工具：web search、browser、RSS、GitHub search。
2. 文件工具：read file、write file、local workspace。
3. 代码工具：Claude Code、Python runner、terminal。
4. 数据工具：PostgreSQL、vector database、object storage。
5. 外部动作工具：Gmail、Calendar、Slack、Telegram、GitHub issue/PR。
6. 记忆工具：knowledge base、experience base、skill store。

工具权限分级：

```text
read_only
write_local
write_memory
write_external
dangerous
```

默认规则：

1. read_only 可自动执行。
2. write_local 可在沙盒目录自动执行。
3. write_memory 需要记录来源和理由。
4. write_external 默认需要审批。
5. dangerous 必须审批，并记录完整审计日志。

### 5.4 Memory

系统将记忆分为三类。

#### Knowledge

事实性资料，例如论文摘要、项目文档、会议信息、网页内容。

字段包括：

```text
title
source
content
summary
tags
created_at
updated_at
reliability_score
related_projects
```

#### Experience

任务执行经验，例如某类任务的有效搜索策略、失败原因、用户偏好、流程问题。

字段包括：

```text
experience_id
task_id
agent_id
problem
lesson
applicable_context
failure_mode
confidence
created_at
used_count
```

#### Skill

可复用能力模块，例如文献调研流程、论文方向评估流程、代码审查流程、会议准备流程。

字段包括：

```text
skill_id
name
trigger_condition
inputs
steps
tools
outputs
failure_modes
approval_policy
version
created_from
last_used_at
```

### 5.5 Approval

Approval 是对高风险动作的人工确认机制。

需要审批的动作包括：

1. 发送邮件。
2. 创建或修改日历会议。
3. 提交 GitHub PR。
4. 删除文件。
5. 修改核心 agent 配置。
6. 修改长期 skill。
7. 对外发布内容。
8. 调用付费或高成本资源。
9. 将低置信内容写入长期记忆。

审批记录包括：

```text
approval_id
requesting_agent
action_type
risk_level
summary
details
created_at
status
user_decision
decision_at
```

## 6. 功能需求

### 6.1 Agent Designer

Agent Designer 用于创建和编辑 agent。

功能包括：

1. 创建 agent。
2. 编辑 agent 名称、角色、目标。
3. 配置 agent 关注的项目。
4. 配置输入源。
5. 配置可用工具。
6. 配置自动动作和需审批动作。
7. 配置运行频率。
8. 配置可读写记忆范围。
9. 配置输出格式。
10. 配置失败处理策略。
11. 生成 Agent Spec。
12. 从已有模板复制 agent。

第一阶段内置模板：

1. Research Agent。
2. Project Manager Agent。
3. Memory Curator Agent。
4. Code Worker Agent。
5. Evaluator Agent。

### 6.2 Task Workspace

Task Workspace 用于查看和管理所有任务。

功能包括：

1. 查看任务列表。
2. 按项目、agent、状态、优先级筛选。
3. 查看任务详情。
4. 查看任务输入、输出和执行日志。
5. 手动创建任务。
6. 暂停、取消、重试任务。
7. 将任务分配给指定 agent。
8. 查看任务依赖关系。
9. 查看任务是否需要审批。
10. 将任务结果转化为知识、经验或技能候选。

任务视图至少包括：

```text
任务标题
所属项目
负责 agent
状态
优先级
创建时间
最近更新时间
下一步动作
是否需要用户处理
```

### 6.3 Agent Workspace

Agent Workspace 用于查看 agent 当前能力和运行状态。

功能包括：

1. 查看 agent 列表。
2. 查看 agent 当前状态。
3. 查看 agent 的目标、工具、权限、记忆访问范围。
4. 查看 agent 正在执行的任务。
5. 查看 agent 历史运行记录。
6. 查看 agent 成本、失败率、成功率。
7. 查看 agent 最近沉淀的经验。
8. 启用或禁用 agent。
9. 手动触发 agent。
10. 修改 agent 配置。

Agent 状态包括：

```text
idle
running
waiting_approval
blocked
disabled
error
```

### 6.4 Tool Registry

Tool Registry 用于管理系统工具。

功能包括：

1. 注册工具。
2. 查看工具说明。
3. 配置工具凭据。
4. 设置工具权限等级。
5. 设置哪些 agent 可以使用该工具。
6. 查看工具调用日志。
7. 禁用高风险工具。
8. 对外部写操作设置审批规则。

工具注册结构：

```yaml
tool_id: gmail_send
name: Send Gmail
type: external_action
risk_level: high
requires_approval: true
allowed_agents:
  - meeting_agent
  - project_manager_agent
```

### 6.5 Memory Workspace

Memory Workspace 用于管理知识库、经验库和技能库。

功能包括：

1. 查看知识条目。
2. 查看经验条目。
3. 查看技能条目。
4. 查看候选记忆。
5. 批准或拒绝写入长期记忆。
6. 合并重复记忆。
7. 标记过时内容。
8. 查看每条记忆的来源任务。
9. 查看某条 skill 的版本历史。
10. 查看某个 agent 使用过哪些 skill。

记忆状态包括：

```text
candidate
approved
active
deprecated
rejected
conflict
```

### 6.6 Approval Center

Approval Center 用于集中处理需要人工确认的动作。

功能包括：

1. 查看待审批动作。
2. 查看动作摘要。
3. 查看完整执行计划。
4. 查看风险等级。
5. 批准、拒绝或要求修改。
6. 对同类动作设置未来默认策略。
7. 查看历史审批记录。

审批风险等级：

```text
low
medium
high
critical
```

### 6.7 Scheduler

Scheduler 用于定时触发 agent 和任务。

功能包括：

1. 创建定时任务。
2. 设置 cron 表达式。
3. 设置运行上下文。
4. 设置失败重试。
5. 查看最近运行情况。
6. 暂停或启用定时任务。

示例：

```yaml
schedule_id: daily_research_scan
agent_id: research_agent_ecg
cron: "0 8 * * *"
task_type: research_scan
enabled: true
```

### 6.8 Run Log and Audit

系统必须记录 agent 的运行过程。

日志包括：

1. agent 何时启动。
2. 输入是什么。
3. 调用了哪些工具。
4. 工具返回了什么。
5. 做了哪些决策。
6. 写入了哪些记忆。
7. 创建了哪些任务。
8. 是否触发审批。
9. 最终输出是什么。
10. 是否失败。

日志用于：

1. 调试 agent。
2. 追踪错误。
3. 评估 agent 表现。
4. 避免错误经验污染。
5. 未来训练或优化 workflow。

## 7. 页面需求

### 7.1 首页 Dashboard

展示：

1. 当前活跃 agent 数量。
2. 正在运行任务。
3. 待审批动作。
4. 今日新增知识。
5. 今日新增经验。
6. 失败任务。
7. 高优先级建议。
8. 本周项目状态。

### 7.2 Agent Designer 页面

包括：

1. agent 基本信息表单。
2. 目标定义。
3. 输入源配置。
4. 工具选择。
5. 权限配置。
6. 记忆访问配置。
7. 触发器配置。
8. 输出格式配置。
9. Agent Spec 预览。
10. 保存与测试按钮。

### 7.3 Task 页面

包括：

1. Kanban 任务板。
2. 任务列表。
3. 任务详情抽屉。
4. agent 分配入口。
5. 执行日志。
6. 任务结果。
7. 转入记忆库按钮。

### 7.4 Agent 页面

包括：

1. agent 列表。
2. agent 状态卡片。
3. agent 能力说明。
4. 工具权限。
5. 当前任务。
6. 最近运行。
7. 成本和失败率。
8. 记忆使用情况。

### 7.5 Memory 页面

包括：

1. Knowledge 列表。
2. Experience 列表。
3. Skill 列表。
4. Candidate Memory 审查队列。
5. 记忆详情。
6. 来源任务链接。
7. 版本历史。

### 7.6 Approval 页面

包括：

1. 待审批动作。
2. 风险等级。
3. 操作摘要。
4. 执行计划。
5. 批准、拒绝、修改按钮。
6. 审批历史。

## 8. 权限和自治等级

系统使用 L0-L4 自治等级。

### L0：只观察

agent 只能读取信息、生成摘要，不能写入长期状态。

允许：

```text
读取网页
读取文件
搜索资料
生成临时摘要
```

### L1：可整理

agent 可以分类、打标签、创建候选记忆。

允许：

```text
创建候选记忆
创建候选任务
生成报告
```

### L2：可内部执行

agent 可以写入内部数据库、更新低风险任务、修改沙盒文件。

允许：

```text
写入知识库
写入经验库
创建内部任务
修改沙盒文件
```

### L3：可建议外部动作

agent 可以准备邮件、会议、PR，但必须审批。

允许：

```text
生成邮件草稿
生成会议邀请草案
生成 PR 草案
提出 skill 修改建议
```

### L4：高自治执行

agent 可自动执行部分外部动作。第一阶段不开放。

## 9. 数据库初步设计

### 9.1 agents

```text
id
name
role
mission
status
autonomy_level
spec_json
created_at
updated_at
```

### 9.2 tasks

```text
id
title
type
project_id
owner_agent_id
status
priority
input_json
output_json
created_by
created_at
updated_at
```

### 9.3 agent_runs

```text
id
agent_id
task_id
status
input_json
output_json
started_at
ended_at
error_message
cost
```

### 9.4 tool_calls

```text
id
run_id
tool_id
input_json
output_json
status
risk_level
created_at
```

### 9.5 memory_items

```text
id
type
title
content
summary
source_task_id
source_run_id
status
confidence
tags
created_at
updated_at
```

### 9.6 skills

```text
id
name
description
trigger_condition
steps_json
tools_json
version
status
created_from_task_id
created_at
updated_at
```

### 9.7 approvals

```text
id
requesting_agent_id
task_id
action_type
risk_level
summary
details_json
status
user_decision
created_at
decided_at
```

### 9.8 schedules

```text
id
agent_id
task_type
cron
input_json
enabled
last_run_at
next_run_at
```

## 10. Agent Factory 编译流程

Agent Factory 需要将用户表单转化为可执行配置。

流程如下：

```text
用户填写 Agent Designer 表单
    ↓
生成 Agent Spec
    ↓
校验 Spec 是否完整
    ↓
生成 Prompt
    ↓
生成 Workflow Graph
    ↓
绑定 Tools
    ↓
绑定 Memory Policy
    ↓
绑定 Approval Policy
    ↓
注册到 Runtime
    ↓
开始运行或等待触发
```

编译产物包括：

1. agent.yaml。
2. system prompt。
3. workflow graph。
4. tool permission config。
5. memory policy。
6. approval policy。
7. schedule config。
8. evaluation rules。

## 11. MVP 范围

第一版只做最小可用系统。

### 必须支持

1. 创建 agent。
2. 编辑 Agent Spec。
3. 创建任务。
4. agent 执行任务。
5. 查看任务状态。
6. 查看 agent 状态。
7. 支持定时触发。
8. 支持 web research 工具。
9. 支持知识库、经验库、技能库的基础写入。
10. 支持审批队列。
11. 支持运行日志。

### 第一版内置 agent

1. Research Agent。
2. Project Manager Agent。
3. Memory Curator Agent。

### 第一版内置任务类型

1. research_scan。
2. project_review。
3. memory_update。
4. task_decomposition。
5. weekly_report。

### 第一版内置工具

1. web_search。
2. browser_fetch。
3. local_file_read。
4. vector_db。
5. postgres_task_db。
6. llm_call。

### 第一版不做

1. Gmail 自动发送。
2. Calendar 自动建会。
3. 自动提交 GitHub PR。
4. agent 自动修改核心代码。
5. 多用户系统。
6. 复杂权限角色。
7. 移动端适配。

## 12. 技术架构建议

第一版技术栈：

```text
Frontend: HTML + Tailwind / React
Backend: Python FastAPI
Agent Runtime: LangGraph or simple custom workflow engine
Database: PostgreSQL
Vector DB: pgvector or Qdrant
Scheduler: cron / Celery Beat / APScheduler
Queue: Celery / Redis Queue
LLM: Claude / OpenAI / OpenRouter
Code Worker: later integrate Claude Code
```

模块划分：

```text
frontend/
  dashboard
  agent_designer
  task_workspace
  memory_workspace
  approval_center

backend/
  api
  agent_runtime
  scheduler
  tool_registry
  memory_manager
  approval_manager
  evaluator

storage/
  postgres
  vector_db
  object_store
```

## 13. 与外部系统的关系

Agent Factory 不需要替代所有现有框架，而是作为控制层后续整合它们。

### Agent Zero

可作为强执行环境或个人 agent 工作台参考。

### LangGraph

可作为复杂 workflow 和状态机 runtime。

### n8n

可作为外部系统连接、定时触发和通知工具。

### Dify

可作为知识库问答界面。

### Claude Code

可作为代码任务 worker。

### Letta

可作为长期记忆和自我更新能力参考。

## 14. 风险与约束

### 14.1 自动化噪声

agent 可能产生大量低价值任务、摘要和记忆。

缓解方式：

1. 引入 relevance score。
2. 引入 novelty score。
3. 设置每日通知上限。
4. 默认进入候选区，不直接打扰用户。

### 14.2 错误记忆污染

agent 可能把错误信息写入长期记忆。

缓解方式：

1. 重要记忆需要来源。
2. 低置信内容进入 candidate 状态。
3. Memory Curator 负责二次审查。
4. 支持记忆废弃和版本回滚。

### 14.3 权限失控

agent 可能执行高风险动作。

缓解方式：

1. 工具权限分级。
2. 外部写操作默认审批。
3. dangerous 工具默认关闭。
4. 所有工具调用写入日志。

### 14.4 框架锁定

如果核心状态放在外部框架内部，后续迁移困难。

缓解方式：

1. 自己维护 Agent Spec。
2. 自己维护任务库。
3. 自己维护记忆库。
4. 外部框架仅作为 adapter。

## 15. 评价指标

### 15.1 agent 运行指标

1. 任务完成率。
2. 失败率。
3. 平均执行时间。
4. 工具调用次数。
5. LLM 成本。
6. 需要人工审批次数。

### 15.2 信息质量指标

1. 新增知识数量。
2. 有效知识比例。
3. 重复知识比例。
4. 经验复用次数。
5. skill 使用次数。
6. 被用户拒绝的建议比例。

### 15.3 用户价值指标

1. 每周减少的手动搜索次数。
2. 每周自动生成的有效任务数量。
3. 每周发现的重要信息数量。
4. 用户采纳建议比例。
5. 用户主动打断或禁用 agent 的次数。

## 16. 开发路线

### Phase 0：需求建模

目标：确定 Agent Spec。

交付：

1. Agent Spec schema。
2. Task schema。
3. Tool schema。
4. Memory schema。
5. Approval schema。

### Phase 1：静态 Agent Designer

目标：通过 HTML 页面收集 agent 需求。

交付：

1. Agent Designer 页面。
2. Agent Spec 生成器。
3. YAML/JSON 导出。

### Phase 2：最小 Runtime

目标：让一个 Research Agent 可以运行。

交付：

1. FastAPI 后端。
2. PostgreSQL。
3. 简单 scheduler。
4. Research Agent 执行逻辑。
5. 任务日志。
6. 结果入库。

### Phase 3：多 Agent 与任务视图

目标：支持 Research Agent、Project Manager Agent、Memory Curator Agent 协作。

交付：

1. Task Workspace。
2. Agent Workspace。
3. 任务分配。
4. 记忆候选队列。
5. 审批队列。

### Phase 4：技能库与经验库

目标：让系统开始沉淀可复用经验。

交付：

1. Experience Store。
2. Skill Store。
3. Skill versioning。
4. 从任务结果生成 skill candidate。

### Phase 5：外部工具集成

目标：接入真实工作工具。

交付：

1. Claude Code worker。
2. GitHub。
3. Gmail draft。
4. Calendar proposal。
5. OpenClaw 或 Telegram 入口。

## 17. 第一版验收标准

第一版完成后，应满足：

1. 用户可以创建一个 Research Agent。
2. 用户可以配置该 agent 的主题、数据源、运行频率和权限。
3. 系统可以定时创建 research_scan 任务。
4. agent 可以执行搜索、摘要、相关性评分。
5. 执行过程可以在任务日志中查看。
6. 高价值结果可以进入候选知识库。
7. Memory Curator 可以审查候选记忆。
8. 用户可以查看 agent 状态和任务状态。
9. 用户可以暂停 agent。
10. 所有工具调用都有日志。

## 18. 长期愿景

Agent Factory 最终应成为个人的 agent construction and operation workspace。

它不只是“创建 agent”，而是管理 agent 的整个生命周期：

```text
定义 agent
→ 生成 agent
→ 运行 agent
→ 分配任务
→ 调用工具
→ 观察结果
→ 审查动作
→ 沉淀知识
→ 总结经验
→ 固化技能
→ 迭代 agent
```

最终系统应支持用户拥有一组长期工作的 agent：

1. Research Agent：负责外部信息发现。
2. Project Manager Agent：负责项目推进。
3. Memory Curator Agent：负责记忆治理。
4. Code Worker Agent：负责代码和实验。
5. Writing Agent：负责文档和论文草稿。
6. Meeting Agent：负责会议准备和议程建议。
7. Evaluator Agent：负责质量检查和失败复盘。

这些 agent 不应只是聊天角色，而应是具备状态、权限、任务、工具和记忆的长期工作单元。
