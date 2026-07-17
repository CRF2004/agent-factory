# Agent Factory NOW

Last updated: 2026-07-17

## 当前阶段

Phase A.2 Persistent Heartbeat Runtime 已完成，PR #2 待合并。

## 当前状态

- PR #1 Autonomous Agent Loop 已合并到 `main`
- 已实现持久化 Agent heartbeat 状态：last/next wakeup、last task、lease、失败计数与错误信息
- 已实现 cooldown，避免 Agent 持续重复创建相同任务
- 已实现 InMemory 与 SQLAlchemy/PostgreSQL heartbeat repository
- 已实现 lease-based 并发保护，防止多个 worker 同时运行同一 Agent
- 已实现失败重试与有上限的指数退避
- 已实现 due-agent 扫描与可选 resident heartbeat runner
- 已增加 heartbeat API：单 Agent 执行、状态读取、批量执行到期 Agent
- Reflection experience 已使用 deterministic fingerprint 去重并更新已有经验
- Alembic revision chain 已修复，并增加 heartbeat state migration
- GitHub Actions 后端测试：18 passed

## 正在做

PR #2 `feat: add persistent autonomous heartbeat runtime` review 与 merge。

## 下一步

1. 合并 PR #2，并在 PostgreSQL 环境执行 `alembic upgrade head`
2. Phase B：Event Bus 与 Agent delegation
3. 增加 Manager Agent、Research Agent、Coding Agent 的协作闭环
4. 在多进程部署前增加 PostgreSQL lease contention 与长期运行测试
5. 后续根据吞吐需求再引入 Redis worker，不提前增加复杂度

## 未决问题

- Tavily 与真实 LLM provider 凭据仍需由部署环境配置
- Resident runner 默认关闭，生产启用频率与 Agent wakeup interval 需按任务成本设置
- 当前 `RuntimeService` 仅执行 `research_scan`，其它 TaskType 仍需逐步接入

## 决策记录

- 保留现有 `RuntimeService`，Autonomous Layer 只负责任务发现、调度与反思
- 不引入 LangGraph 或新的 workflow engine
- Heartbeat runner 默认关闭，手动 API 始终可用
- 使用数据库 lease 处理多进程重复执行，不依赖进程内锁作为生产保证
- Experience memory 使用确定性 fingerprint 去重，不在此阶段引入向量相似度合并
- Redis 延后到需要独立 worker 和更高吞吐的阶段
