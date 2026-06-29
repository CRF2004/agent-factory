# Agent Factory Development Plan

## 目标

构建一个用于长期常驻个人 agent 的创建、运行、管理和迭代工作台。第一版重点不是集成所有外部系统，而是建立清晰的 Agent Spec、任务运行闭环、审批机制、运行日志和基础管理界面。

## MVP 边界

### 必须完成

- Agent Spec / Task / Tool / Memory / Approval / Schedule 的标准化 schema。
- 可创建和编辑 Agent Spec 的 Agent Designer。
- 可创建、排队、运行、查看状态的 Task 系统。
- 至少一个可运行的 Research Agent。
- 基础 Scheduler，支持按 cron 或 interval 创建任务。
- Tool Registry，至少支持 `web_search`、`browser_fetch`、`local_file_read`、`llm_call` 的抽象接口。
- Memory Store，支持 knowledge、experience、skill 和 candidate memory。
- Approval Center，所有外部写动作和高风险动作默认进入审批队列。
- Run Log / Audit，记录 agent run、tool call、决策、输出和错误。

### 第一版不做

- 多用户权限体系。
- Gmail / Calendar / GitHub PR 的真实自动执行。
- Agent 自动修改核心代码。
- L4 高自治执行。
- 复杂多模态能力。
- 对所有 agent 框架的兼容。

## 架构原则

1. **Agent Spec 是核心资产**
   - 所有 agent 配置先落到自有 schema。
   - LangGraph、Claude Code、n8n、Dify、Letta 等只能作为 adapter，不持有核心状态。

2. **任务驱动运行**
   - agent 不直接“自由行动”，而是通过 task、schedule、approval、tool call 构成可追踪闭环。
   - 每次执行必须生成 `agent_run` 和日志。

3. **默认低风险自治**
   - read-only 和内部低风险写入可以自动执行。
   - 外部写操作、dangerous 工具、低置信长期记忆必须审批。

4. **记忆先候选后沉淀**
   - 重要内容先进入 candidate memory。
   - Memory Curator 或用户审批后再进入长期知识库、经验库或技能库。

5. **先简单 runtime，后复杂 workflow**
   - MVP 优先自定义轻量 workflow engine。
   - 当任务图和多 agent 协作复杂度上升后，再引入 LangGraph。

## 推荐技术栈

- Frontend: React + Tailwind。
- Backend: Python FastAPI。
- Database: PostgreSQL。
- Vector: pgvector 优先，后续可替换 Qdrant。
- Scheduler: APScheduler 起步，后续可替换 Celery Beat。
- Queue: MVP 可先同步/轻队列，后续引入 Redis Queue 或 Celery。
- Runtime: 自定义 task runner 起步，保留 LangGraph adapter 接口。
- LLM: 通过统一 `llm_call` tool adapter 接入 OpenAI / Claude / OpenRouter。

## 目录规划

```text
cc_dump/agent_factory/
  plan.md
  NOW.md
  requirements.md
  backend/
    app/
      api/
      core/
      schemas/
      models/
      services/
      agent_runtime/
      tool_registry/
      memory_manager/
      approval_manager/
      scheduler/
    tests/
  frontend/
    src/
      pages/
      components/
      api/
      state/
  storage/
    migrations/
    seeds/
  specs/
    agent_spec.schema.json
    task.schema.json
    tool.schema.json
    memory.schema.json
    approval.schema.json
  docs/
    architecture.md
    runtime.md
```

## Phase 0: 需求建模与 Schema

目标：把需求文档转化为可校验的数据模型。

交付：

- `specs/agent_spec.schema.json`
- `specs/task.schema.json`
- `specs/tool.schema.json`
- `specs/memory.schema.json`
- `specs/approval.schema.json`
- `specs/schedule.schema.json`
- 后端 Pydantic models。
- 数据库 ERD / migration 初稿。
- 内置 agent templates：Research Agent、Project Manager Agent、Memory Curator Agent。

验收：

- 可以用 schema 校验一个完整 Research Agent Spec。
- 可以从模板生成默认 Agent Spec。
- schema 覆盖自治等级、工具权限、记忆策略和审批策略。

## Phase 1: 静态 Agent Designer

目标：用户可以通过页面创建和编辑 Agent Spec。

交付：

- Agent Designer 页面。
- Agent 基本信息、目标、输入源、工具、权限、记忆、触发器表单。
- Agent Spec JSON/YAML 预览。
- 保存 Agent Spec 到后端。
- 从模板复制 agent。

验收：

- 用户可以创建 Research Agent。
- 用户可以配置主题、数据源、运行频率和权限。
- 保存后的 spec 可以通过 schema 校验。

## Phase 2: 最小 Runtime

目标：让一个 Research Agent 真正执行一次 `research_scan`。

交付：

- FastAPI 后端基础结构。
- PostgreSQL 表：agents、tasks、agent_runs、tool_calls、memory_items、approvals、schedules。
- Task 创建、查询、状态更新 API。
- Agent Run 执行器。
- Tool adapter 抽象。
- `web_search`、`browser_fetch`、`llm_call` 的最小实现或 mockable interface。
- Research Agent workflow：搜索、抓取、摘要、相关性评分、候选记忆生成。
- 运行日志和错误记录。

验收：

- 手动创建 `research_scan` task 后，Research Agent 可以执行并产出结果。
- 每次执行有 `agent_run`、`tool_calls` 和 final output。
- 高价值结果可以进入 candidate memory。

## Phase 3: Scheduler、Workspace 与审批

目标：形成日常可用的 agent operation workspace。

交付：

- Scheduler，按配置创建任务。
- Dashboard：首页统计活跃 agent、运行任务、待审批、失败任务、今日新增记忆。
- Task Workspace：列表、筛选、详情、日志、重试、取消。
- Agent Workspace：agent 状态、工具权限、当前任务、历史运行。
- Approval Center：待审批列表、风险等级、详情、批准、拒绝。
- Memory Workspace：candidate memory 审查、knowledge / experience / skill 基础列表。

验收：

- Research Agent 可按计划自动创建任务。
- 用户可在页面查看任务、日志和候选记忆。
- 需要审批的动作不会自动执行。

## Phase 4: 多 Agent 协作

目标：支持 Research Agent、Project Manager Agent、Memory Curator Agent 的基础协作。

交付：

- Project Manager Agent template 与 `project_review` workflow。
- Memory Curator Agent template 与 `memory_update` workflow。
- 任务分配与任务依赖。
- 从任务结果创建后续任务。
- candidate memory 到长期 memory 的审查流程。

验收：

- Research Agent 可以创建候选记忆或候选任务。
- Memory Curator 可以审查候选记忆并写入长期库。
- Project Manager 可以读取任务状态并生成项目报告。

## Phase 5: 经验库与技能库

目标：系统开始沉淀可复用经验和流程。

交付：

- Experience Store。
- Skill Store。
- Skill versioning。
- 从任务复盘生成 experience candidate。
- 从高复用流程生成 skill candidate。
- Skill 使用记录和版本历史。

验收：

- 任务失败或成功后可沉淀经验。
- 可把稳定流程固化为 skill。
- agent run 可引用已有 skill。

## Phase 6: 外部工具 Adapter

目标：在审批保护下接入真实外部工作流。

交付：

- Claude Code worker adapter。
- GitHub issue / PR draft adapter。
- Gmail draft adapter。
- Calendar proposal adapter。
- Telegram / OpenClaw 入口调研或原型。

验收：

- 外部写动作默认进入审批队列。
- 所有外部工具调用有完整审计日志。
- Code Worker 只能在分配目录和权限内工作。

## 关键数据状态

### Task 状态

```text
created -> queued -> running -> completed
created -> queued -> running -> waiting_approval -> completed
created -> queued -> running -> failed
created -> cancelled
running -> blocked
```

### Agent 状态

```text
idle
running
waiting_approval
blocked
disabled
error
```

### Memory 状态

```text
candidate
approved
active
deprecated
rejected
conflict
```

### Approval 状态

```text
pending
approved
rejected
needs_revision
expired
```

## 优先实现顺序

1. Schema 与 Pydantic models。
2. 数据库 migration。
3. Agent / Task / Run / ToolCall CRUD API。
4. Agent templates。
5. Research Agent 最小 workflow。
6. 运行日志。
7. Memory candidate。
8. Scheduler。
9. Agent Designer。
10. Task / Agent / Memory / Approval 页面。

## 主要风险

- 自动化噪声：通过 relevance score、novelty score、每日上限和 candidate queue 缓解。
- 错误记忆污染：长期记忆必须记录来源、置信度和审查状态。
- 权限失控：工具分级、审批策略和完整审计日志必须先于外部动作实现。
- 框架锁定：核心状态必须留在本项目数据库和 spec 中。
- Runtime 过早复杂化：先用明确可调试的 custom workflow，避免一开始引入过重抽象。

## 第一版验收清单

- 用户可以创建一个 Research Agent。
- 用户可以配置主题、数据源、运行频率和权限。
- 系统可以定时创建 `research_scan` 任务。
- agent 可以执行搜索、摘要、相关性评分。
- 执行过程可以在任务日志中查看。
- 高价值结果可以进入候选知识库。
- Memory Curator 可以审查候选记忆。
- 用户可以查看 agent 状态和任务状态。
- 用户可以暂停 agent。
- 所有工具调用都有日志。
