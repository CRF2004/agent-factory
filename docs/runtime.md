# MVP Runtime Slice

The current runtime is intentionally minimal and in-memory. It validates the core Agent Factory loop before adding PostgreSQL, queues, or external tools.

## Current Flow

```text
Research Agent template
  -> create research_scan task
  -> run task manually
  -> create agent_run
  -> create mock web_search tool_call
  -> create mock llm_call tool_call
  -> create candidate knowledge memory
  -> mark task completed
```

## API Surface

All routes are mounted under `/api`.

- `GET /health`
- `POST /agents`
- `GET /agents`
- `GET /agents/{agent_id}`
- `POST /tasks`
- `GET /tasks`
- `GET /tasks/{task_id}`
- `POST /tasks/{task_id}/run`
- `GET /runs`
- `GET /tool-calls`
- `GET /memory-items`
- `GET /approvals`

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

Example task payload:

```json
{
  "task_id": "task_runtime_001",
  "title": "Search ECG audit papers",
  "type": "research_scan",
  "owner_agent": "research_agent_default",
  "project_id": "ecg_audit",
  "priority": "high",
  "input": {
    "topics": ["ECG audit", "medical AI safety"],
    "sources": ["mock_web"]
  },
  "expected_output": ["paper_candidates", "relevance_scores"]
}
```

## Known Limitations

- State is process-local and resets when the server restarts.
- Tool calls are mock implementations.
- Only `research_scan` is executable.
- Approval objects are listed but not created by the runtime yet.
- Route-level tests using `TestClient` hang in the current environment, so tests currently validate app construction and service-level runtime behavior.
