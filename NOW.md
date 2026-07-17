# Agent Factory NOW

Last updated: 2026-07-17

## 当前阶段

PR #2 Persistent Heartbeat Runtime 已合并。项目进入 Mobile Operations Console 阶段。

## 当前状态

- PR #1 Autonomous Agent Loop 已合并到 `main`
- PR #2 Persistent Heartbeat Runtime 已合并到 `main`
- 已实现 Wakeup -> Planner -> Task -> Runtime -> Reflection -> Experience Memory
- 已实现持久化 Agent heartbeat 状态：last/next wakeup、last task、lease、失败计数与错误信息
- 已实现 cooldown，避免 Agent 持续重复创建相同任务
- 已实现 InMemory 与 SQLAlchemy/PostgreSQL heartbeat repository
- 已实现 lease-based 并发保护，防止多个 worker 同时运行同一 Agent
- 已实现失败重试与有上限的指数退避
- 已实现 due-agent 扫描与可选 resident heartbeat runner
- 已增加 heartbeat API：单 Agent 执行、状态读取、批量执行到期 Agent
- Reflection experience 已使用 deterministic fingerprint 去重并更新已有经验
- Alembic revision chain 已修复，并增加 heartbeat state migration
- GitHub Actions 后端测试基线：18 passed
- 已有 React + TypeScript + Vite + Tailwind 像素风管理前端，但当前布局仍以桌面固定侧栏为主

## 正在做

开发工作将迁移到服务器上的 Agent 继续推进。

当前产品方向：

```text
Secure Operations API
  -> Mobile-first Responsive Web UI
  -> Android WebView App
  -> Runtime Observability
  -> Multi-Agent Organization
```

## 下一步

1. 在服务器拉取最新 `main`
2. 执行 `pytest backend/tests -v`
3. PostgreSQL 环境执行 `alembic upgrade head`
4. 创建 `feature/mobile-agent-operations` 分支
5. 实施 Secure Operations API：认证、overview 聚合接口、Agent activity、pause/resume
6. 将固定桌面侧栏改成 responsive shell，手机端使用底部导航
7. Dashboard 增加 heartbeat、last/next wakeup、失败状态和 Wake Now
8. 使用 Capacitor 将现有 React 前端包装成 Android WebView App
9. 增加 activity event log 与 SSE 后，再进入 Multi-Agent Event Bus

## 当前移动端 MVP 范围

手机端第一版支持：

- 查看全部 Agent 状态
- 查看 last / next wakeup
- 查看当前任务、最近运行和失败原因
- Wake Now
- Pause / Resume
- 查看与处理审批
- 查看最近 Memory

手机端第一版不优先实现：

- 复杂 Agent Designer 表单
- 原生 Android 业务页面
- 多账号
- Google Play 发布
- 后台 Android Service

## 未决问题

- Tavily 与真实 LLM provider 凭据需要在服务器环境配置
- Resident runner 生产 wakeup interval 需要按任务成本设置
- 当前 `RuntimeService` 仅执行 `research_scan`，其它 TaskType 仍需逐步接入
- 远程访问必须先完成认证和 HTTPS，不能直接把未认证 API 暴露到公网
- Android 第一版使用打包后的 React 静态资源还是远程加载页面；当前建议打包 UI、通过 HTTPS API 获取实时状态
- 推送通知暂不进入第一版，后续可增加 Agent failure 和 pending approval 通知

## 决策记录

- 保留现有 `RuntimeService`，Autonomous Layer 只负责任务发现、调度与反思
- 不引入 LangGraph 或新的 workflow engine
- Heartbeat runner 默认关闭，部署环境显式启用
- 使用数据库 lease 处理多进程重复执行
- Experience memory 使用确定性 fingerprint 去重
- Redis / Celery 延后到需要独立 worker 和更高吞吐的阶段
- 优先构建移动端可观察性，再扩展 Manager / Research / Coding Agent 协作
- 复用现有 React 前端，Android 采用 Capacitor/WebView 容器，不维护第二套 UI
- 手机端第一版定位为 read-mostly operations console，只提供少量明确、安全的控制动作

## 服务器 Agent 接手入口

阅读顺序：

```text
CLAUDE.md
NOW.md
plan.md
backend/app/agent_runtime/README.md
```

启动目标：

```text
创建 feature/mobile-agent-operations
先实施 Secure Operations API，再改造 mobile-first UI。
不要直接跳到 Multi-Agent。
```
