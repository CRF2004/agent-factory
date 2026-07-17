# Autonomous Agent Runtime

The autonomous layer remains on top of the existing `RuntimeService`:

`WakeupLoop -> Planner -> Task creation -> RuntimeService -> ReflectionEngine -> experience memory`

The persistent heartbeat layer adds scheduling, cooldown, leases, retry state, and an optional resident runner:

`HeartbeatService -> AutonomousRuntime.run_once() -> persisted AgentHeartbeatState`

## API

```text
POST /api/agents/{agent_id}/heartbeat
GET  /api/agents/{agent_id}/heartbeat
POST /api/agents/heartbeat/run-due
```

Use `?force=true` on the single-agent heartbeat endpoint to bypass the cooldown. Lease protection still applies.

## Configuration

```text
AGENT_FACTORY_HEARTBEAT_ENABLED=false
AGENT_FACTORY_HEARTBEAT_POLL_SECONDS=30
AGENT_FACTORY_DEFAULT_WAKEUP_SECONDS=3600
AGENT_FACTORY_HEARTBEAT_LEASE_SECONDS=300
```

The resident runner is disabled by default. Manual API heartbeats remain available when it is disabled.

## Validation

Run the demo from the repository root:

```bash
python demo.py
```

Run the autonomous and heartbeat tests:

```bash
pytest backend/tests/test_autonomous_runtime.py \
       backend/tests/test_heartbeat_runtime.py \
       backend/tests/test_heartbeat_sqlalchemy.py \
       backend/tests/test_heartbeat_api.py
```
