CREATE TABLE IF NOT EXISTS agent_heartbeat_states (
    agent_id TEXT PRIMARY KEY REFERENCES agents(id) ON DELETE CASCADE,
    next_wakeup_at TEXT,
    lease_token TEXT,
    lease_until TEXT,
    state_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_heartbeat_states_next_wakeup_at
    ON agent_heartbeat_states(next_wakeup_at);

CREATE INDEX IF NOT EXISTS idx_agent_heartbeat_states_lease_until
    ON agent_heartbeat_states(lease_until);
