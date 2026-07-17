# Agent Factory Development Plan

Last updated: 2026-07-17

## 1. 产品目标

Agent Factory 的目标是构建一个长期驻留的 Agent Organization Runtime：Agent 能被周期性唤醒，主动发现任务，执行、反思并积累经验；用户可以在桌面和手机上随时查看运行状态、处理异常与审批。

核心生命周期：

```text
Observe
  -> Think
  -> Plan
  -> Act
  -> Reflect
  -> Learn
  -> Sleep / Next Wakeup
```

目标形态：

```text
                  Agent Factory Runtime

                       Manager Agent

                            |
          ---------------------------------------
          |                  |                  |
    Research Agent      Coding Agent      Analyst Agent

                            |
              Memory / Experience / Skill

                            |
              Mobile Operations Console
```

## 2. 当前已完成基线

以下能力已经进入 `main`：

### PR #1: Autonomous Agent Loop

- `WakeupLoop`
- 确定性 `Planner`
- 自动创建 Task
- 复用现有 `RuntimeService.run_task()`
- `ReflectionEngine`
- `MemoryItem(type="experience")`
- Autonomous Runtime 单次完整闭环

### PR #2: Persistent Heartbeat Runtime

- 持久化 `AgentHeartbeatState`
- `last_wakeup_at` / `next_wakeup_at`
- cooldown 防重复任务
- database lease 防重复执行
- due-agent 扫描
- 失败重试与指数退避
- 可选 resident heartbeat runner
- heartbeat REST API
- Experience Memory fingerprint 去重
- PostgreSQL / SQLAlchemy 持久化
- Alembic heartbeat migration
- GitHub Actions 后端测试

当前运行链路：

```text
HeartbeatService
  -> acquire lease
  -> WakeupLoop
  -> Planner
  -> Task creation
  -> RuntimeService
  -> ReflectionEngine
  -> Experience Memory
  -> persist next_wakeup_at
```

当前自动化测试基线：

```text
18 passed
```

## 3. 当前产品决策

### 3.1 先做可观察、可控制，再扩展 Multi-Agent

下一阶段不直接进入复杂的 Manager / Research / Coding Agent 协作。

优先完成：

```text
安全远程访问
  -> Mobile-first Operations Console
  -> Android WebView App
  -> 运行可观察性
  -> Multi-Agent Event Bus
```

原因：常驻 Agent 在扩展数量和自治能力前，必须先让用户随时知道：

- 哪些 Agent 正在运行
- 最近做了什么
- 下次何时唤醒
- 是否失败或阻塞
- 是否有待审批动作
- 是否需要人工强制唤醒、暂停或恢复

### 3.2 Web 是主界面，Android 是轻量容器

保留现有 React + TypeScript + Vite + Tailwind 前端，改造为 mobile-first responsive Web App。

Android 第一版使用 WebView 容器，优先采用 Capacitor 接入现有前端工程，不重新开发一套原生 UI。

建议目录：

```text
frontend/
  src/
  android/          # Capacitor Android project
```

同一套前端同时支持：

- 桌面浏览器
- 手机浏览器
- Android App

Android App 第一版打包前端静态资源，通过 HTTPS API 连接服务器。UI 代码更新时重新构建 APK；Agent 实时状态直接从服务器获取。

### 3.3 手机端第一版以监控和安全操作为主

手机端第一版不承担复杂 Agent Designer 表单。

优先支持：

- 查看所有 Agent 状态
- 查看 heartbeat 状态
- 查看当前任务和最近运行
- 查看失败原因
- 手动唤醒
- 暂停 / 恢复 Agent
- 查看和处理审批
- 查看最近新增 Memory

Agent 创建、复杂 Tool 权限配置和长表单编辑仍以桌面端为主。

## 4. 下一阶段：Phase C Mobile Operations Console

建议分支：

```text
feature/mobile-agent-operations
```

建议拆分为 4 个可独立合并的 PR。

---

## PR #3: Secure Operations API

### 目标

在服务器暴露给手机前，建立最小安全边界和适合移动端消费的聚合 API。

### 必须完成

#### 身份认证

第一版至少实现单用户认证：

- 登录接口或预配置管理员账号
- 短期 access token
- 后端所有 operations API 默认需要认证
- `/api/health` 可保持公开
- 密码、token signing secret 仅通过环境变量配置

不要把固定 API token 写入前端源码或 Android 包。

#### HTTPS 与网络边界

生产部署要求：

- Caddy 或 Nginx 终止 HTTPS
- 只开放 443
- PostgreSQL 不暴露公网
- CORS 使用明确 allowlist
- 可选使用 VPN / Tailscale，仅允许个人设备访问

#### 聚合 API

新增适合首页一次加载的接口：

```text
GET /api/operations/overview
```

建议响应：

```json
{
  "summary": {
    "total_agents": 4,
    "running_agents": 1,
    "failed_agents": 0,
    "pending_approvals": 2,
    "running_tasks": 1
  },
  "agents": [
    {
      "agent_id": "research-agent",
      "name": "Research Agent",
      "status": "idle",
      "last_wakeup_at": "...",
      "next_wakeup_at": "...",
      "last_task_id": "...",
      "consecutive_failures": 0,
      "last_error": null,
      "active_task": null
    }
  ]
}
```

新增 Agent 活动接口：

```text
GET /api/agents/{agent_id}/activity?limit=30
```

聚合最近的：

- heartbeat
- task
- run
- tool call
- memory
- approval

第一版可以从已有表查询并构造时间线，不需要先实现 Event Bus。

#### 控制 API

新增明确动作端点：

```text
POST /api/agents/{agent_id}/heartbeat?force=true
POST /api/agents/{agent_id}/pause
POST /api/agents/{agent_id}/resume
```

暂停和恢复必须记录审计信息。

### 验收

- 未认证访问 operations API 返回 401
- 手机首页只需一次 overview 请求即可展示核心状态
- 可按 Agent 查询最近活动
- force heartbeat 不绕过 lease
- pause 后 resident runner 不再执行该 Agent
- 后端原有测试保持通过

---

## PR #4: Mobile-first Responsive Web UI

### 目标

将当前桌面像素风工作台改造成手机可用的 Operations Console，同时保留桌面布局。

### 当前需要修复的问题

现有 `PixelLayout` 使用固定 `w-52` 左侧栏，不适合手机屏幕。

现有 Dashboard 主要统计 Task 和 Memory，没有展示 heartbeat、下次唤醒时间、连续失败和 last error。

### Shell 改造

桌面：

```text
Left Sidebar + Main Content
```

手机：

```text
Top Status Bar
Main Content
Bottom Navigation
```

手机底部导航建议：

```text
Overview
Agents
Tasks
Approvals
More
```

要求：

- 支持 320px 以上宽度
- 支持 Android safe-area inset
- 触控区域至少约 44px
- 不依赖 hover 才能操作
- 页面不得横向溢出
- 手机端主要信息一屏可扫读

### Overview 页面

顶部状态摘要：

```text
Agents Online
Running Tasks
Failures
Approvals
```

Agent 状态卡必须显示：

- name / role
- status
- last wakeup
- next wakeup
- active task
- consecutive failures
- last error 摘要
- Wake Now 操作

### Agent Detail 页面

展示：

- mission
- autonomy level
- enabled tools
- heartbeat state
- 当前任务
- 最近 activity timeline
- recent experience memory

控制：

- Wake Now
- Pause
- Resume

危险操作需要二次确认。

### 数据刷新

第一版采用 React Query polling：

```text
Overview: 10-15 seconds
Agent detail: 10-30 seconds
Task detail: running 时 5-10 seconds
```

浏览器进入后台后降低刷新频率。

SSE / WebSocket 延后到后续 observability PR。

### 状态处理

所有页面必须有：

- loading
- empty
- offline / request failed
- retry
- stale data 提示

### 验收

- Chrome Android 模拟尺寸无横向滚动
- 桌面侧栏仍可用
- 手机底部导航可单手操作
- 用户在两次点击内进入任一 Agent 详情
- 用户可以看到 last / next wakeup 和失败状态
- 用户可以执行 Wake Now、Pause、Resume

---

## PR #5: Android WebView App

### 目标

把 mobile-first Web UI 包装成可安装的 Android App。

### 技术方案

在 `frontend/` 中接入 Capacitor Android：

```text
frontend/android/
```

App 使用同一份 React 构建产物，并通过配置连接服务器 HTTPS API。

### 第一版能力

- App 启动进入登录页或 Overview
- 保持登录状态
- Android 返回键正确处理前端路由
- 外部链接交给系统浏览器
- 加载失败时提供重试页
- 网络恢复后可重新加载
- 支持深色主题和系统 safe area
- Debug APK 可在个人 Android 设备安装

### 暂不实现

- Google Play 发布
- 多账号
- 复杂原生页面
- 后台常驻 Android Service
- 离线执行 Agent
- 原生数据库同步

### 可选后续能力

- Firebase Cloud Messaging 推送
- Agent 失败通知
- 待审批通知
- Android biometric unlock
- 分享内容到 Agent Factory

### 验收

- 可生成 debug APK
- 真机可以登录服务器
- 可以查看 Agent 实时状态
- 可以安全执行 Wake Now / Pause / Resume
- 网络异常不会白屏
- Web 版本和 Android 版本共享主要 UI 代码

---

## PR #6: Runtime Observability

### 目标

让常驻 Agent 的运行变化更接近实时，并具备可诊断性。

### 交付

- 统一 activity/event schema
- Agent activity feed
- heartbeat duration
- task duration
- failure reason 分类
- tool call latency
- 最近一次成功运行时间
- SSE event stream
- 前端实时更新
- 告警规则基础结构

建议事件：

```text
heartbeat_started
heartbeat_skipped
heartbeat_failed
task_created
task_started
task_completed
task_failed
memory_created
approval_created
agent_paused
agent_resumed
```

事件总线第一版可使用数据库 event log，不必立即引入 Redis。

### 验收

- 手机页面可实时看到 Agent 状态变化
- 每次 Agent 行为有可查询事件
- 用户可以定位失败发生在哪个 lifecycle 阶段

## 5. 后续：Phase D Multi-Agent Organization

只有当 Mobile Operations Console 和 Observability 稳定后，再进入多 Agent 协作。

建议顺序：

### PR #7: Event Bus and Delegation

- Event Bus interface
- task_created / task_completed / memory_created 事件
- Agent delegation schema
- 父子任务与依赖
- 防循环委派

### PR #8: Manager Agent

- Manager Agent template
- 读取组织状态
- 评估 Research Agent 结果
- 创建后续任务
- 任务优先级调整

### PR #9: Coding Agent

- 受限工作目录
- 明确 tool permissions
- 输出 patch / draft PR
- 外部写入默认审批

### PR #10: Memory Curator

- candidate memory 审查
- experience 合并
- skill candidate 提取
- memory 冲突检测

## 6. 部署计划

服务器最小部署：

```text
Caddy / Nginx
  -> React static frontend
  -> FastAPI
  -> PostgreSQL + pgvector
  -> Resident Heartbeat Runner
```

建议配置：

```text
AGENT_FACTORY_REPOSITORY_BACKEND=postgres
AGENT_FACTORY_DATABASE_URL=...
AGENT_FACTORY_HEARTBEAT_ENABLED=true
AGENT_FACTORY_HEARTBEAT_POLL_SECONDS=30
AGENT_FACTORY_DEFAULT_WAKEUP_SECONDS=3600
AGENT_FACTORY_HEARTBEAT_LEASE_SECONDS=300
```

部署步骤：

```bash
alembic upgrade head
pytest backend/tests -v
npm --prefix frontend ci
npm --prefix frontend run build
```

上线前必须验证：

- HTTPS
- authentication
- database backup
- log rotation
- heartbeat runner 单实例或 lease contention
- 服务重启后 heartbeat state 恢复
- Android 设备可访问 API

## 7. 关键开发原则

不要：

- 重写 `RuntimeService`
- 在可观察性完成前快速堆叠大量 Agent
- 过早引入 LangGraph
- 过早引入 Redis / Celery
- 为 Android 重新开发一套业务 UI
- 将 API key 或固定管理员 token 打包进前端
- 直接把未认证 FastAPI 暴露到公网

保持：

```text
Existing RuntimeService
        |
Autonomous / Heartbeat Layer
        |
Operations API
        |
Responsive Web UI
        |
Android WebView Shell
```

每个 PR：

- 只包含一个逻辑阶段
- 增加对应测试
- 更新 `NOW.md`
- GitHub Actions 通过后再合并

## 8. 当前立即执行顺序

服务器 Agent 应按以下顺序继续：

```text
1. 拉取 main，确认包含 PR #2 merge commit
2. 运行全部 backend tests
3. PostgreSQL 执行 alembic upgrade head
4. 创建 feature/mobile-agent-operations 分支
5. 实施 PR #3 Secure Operations API
6. 实施 PR #4 Mobile-first Responsive Web UI
7. 实施 PR #5 Android WebView App
8. 实施 PR #6 Runtime Observability
9. 再进入 Multi-Agent Event Bus
```

## 9. 服务器 Agent 启动指令

```text
继续开发 CRF2004/agent-factory。

先阅读 CLAUDE.md、NOW.md、plan.md，以及 backend/app/agent_runtime/README.md。

当前 main 已包含：
- Autonomous Agent Loop
- Persistent Heartbeat Runtime

不要重新设计 RuntimeService，不引入 LangGraph，不提前引入 Redis/Celery。

当前目标是 Mobile Operations Console：
1. Secure Operations API
2. Mobile-first responsive React UI
3. Android Capacitor/WebView shell
4. Runtime observability

必须优先保证认证、HTTPS 部署边界和移动端可观察性，再进入 Multi-Agent。

每完成一个逻辑单元：
- 运行 pytest backend/tests -v
- 运行前端 build / lint
- 更新 NOW.md
- 提交独立 commit
- 创建 draft PR
```
