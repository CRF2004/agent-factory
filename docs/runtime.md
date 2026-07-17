# Agent Factory Runtime

The runtime supports both manual task execution and persistent autonomous heartbeats. The autonomous layer creates tasks but continues to execute them through the existing `RuntimeService`.

## Autonomous Flow

```text
HeartbeatService
  -> acquire per-agent lease
  -> WakeupLoop observation
  -> Planner decision
  -> create TaskSpec when action is needed
  -> RuntimeService.run_task()
  -> ReflectionEngine
  -> knowledge + deduplicated experience memory
  -> persist next_wakeup_at
  -> release lease
```

Heartbeat state records:

- last wakeup and last action timestamps
- next wakeup timestamp
- last autonomous task
- current lease token and expiry
- consecutive failure count and last error

## API Surface

All routes are mounted under `/api`.

- `GET /health`
- `POST /agents`
- `GET /agents`
- `GET /agents/{agent_id}`
- `POST /agents/{agent_id}/heartbeat`
- `GET /agents/{agent_id}/heartbeat`
- `POST /agents/heartbeat/run-due`
- `POST /tasks`
- `GET /tasks`
- `GET /tasks/{task_id}`
- `POST /tasks/{task_id}/run`
- `GET /runs`
- `GET /tool-calls`
- `GET /memory-items`
- `GET /approvals`

`POST /agents/{agent_id}/heartbeat?force=true` bypasses the cooldown but does not bypass the execution lease.

## Configuration

```text
AGENT_FACTORY_HEARTBEAT_ENABLED=false
AGENT_FACTORY_HEARTBEAT_POLL_SECONDS=30
AGENT_FACTORY_DEFAULT_WAKEUP_SECONDS=3600
AGENT_FACTORY_HEARTBEAT_LEASE_SECONDS=300
```

The resident background runner is disabled by default. The heartbeat API remains usable when it is disabled.

## Run Locally

In-memory mode:

```bash
PYTHONPATH=backend uvicorn app.main:app --reload
```

PostgreSQL mode:

```bash
export AGENT_FACTORY_DATABASE_URL='postgresql+psycopg://agent_factory:agent_factory@localhost:5432/agent_factory'
PYTHONPATH=backend alembic upgrade head
PYTHONPATH=backend AGENT_FACTORY_REPOSITORY_BACKEND=postgres uvicorn app.main:app --reload
```

Enable the resident runner:

```bash
export AGENT_FACTORY_HEARTBEAT_ENABLED=true
PYTHONPATH=backend uvicorn app.main:app
```

## Operational Behavior

- A future `next_wakeup_at` returns `no_action` without creating a task.
- An unexpired lease returns `already_running`.
- Runtime failures are stored in heartbeat state and retried with bounded exponential backoff.
- Disabled agents are skipped by due-agent scans.
- Repeated equivalent reflections update one experience memory instead of creating duplicates.

## Current Limitations

- Only `research_scan` is executable by `RuntimeService`.
- The resident runner is process-local; PostgreSQL leases prevent duplicate work across processes, but polling coordination is intentionally simple.
- LLM and web-search providers fall back to mocks when credentials are not configured.
