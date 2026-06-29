# PostgreSQL Persistence

The default development mode is still in-memory if no database URL is configured. To persist agent/task/run/tool/memory state across restarts, run with the SQLAlchemy repository and PostgreSQL.

## Install Dependencies

```bash
pip install -e '.[dev]'
```

If this server needs a local proxy for package installation, use port `7893`:

```bash
export HTTP_PROXY='http://127.0.0.1:7893'
export HTTPS_PROXY='http://127.0.0.1:7893'
pip install -e '.[dev]'
```

This installs:

- SQLAlchemy
- Alembic
- psycopg
- FastAPI runtime dependencies
- pytest

## Configure Database

Example local URL:

```bash
export AGENT_FACTORY_DATABASE_URL='postgresql+psycopg://agent_factory:agent_factory@localhost:5432/agent_factory'
export AGENT_FACTORY_REPOSITORY_BACKEND=postgres
```

## Run Migrations

```bash
PYTHONPATH=backend alembic upgrade head
```

Alembic reads `AGENT_FACTORY_DATABASE_URL`. The fallback `sqlalchemy.url` in `alembic.ini` is a placeholder and should not be used directly.

## Start API

```bash
PYTHONPATH=backend uvicorn app.main:app --reload
```

When `AGENT_FACTORY_REPOSITORY_BACKEND=postgres`, the app uses `SQLAlchemyRepository` and persists:

- agents
- tasks
- agent_runs
- tool_calls
- memory_items
- approvals
- schedules

Built-in agent templates are upserted at startup.

## Test Persistence Without PostgreSQL

The test suite uses a file-backed SQLite database to validate repository persistence semantics:

```bash
pytest -q backend/tests/test_sqlalchemy_repository.py
```

This does not replace PostgreSQL integration testing, but it verifies that the repository no longer depends on process-local memory.

You can also validate Alembic itself against a temporary SQLite database:

```bash
AGENT_FACTORY_DATABASE_URL=sqlite:////tmp/agent_factory_alembic_check.db PYTHONPATH=backend alembic upgrade head
```
