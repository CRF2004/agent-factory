# Phase 0 Database Design

## agents

| Column | Type | Notes |
| --- | --- | --- |
| id | text primary key | Stable agent id |
| name | text | Display name |
| role | text | Agent role |
| mission | text | Long-running objective |
| status | text | idle/running/waiting_approval/blocked/disabled/error |
| autonomy_level | text | L0-L4, L4 disabled in MVP |
| spec_json | jsonb | Full Agent Spec |
| created_at | timestamptz | |
| updated_at | timestamptz | |

## tasks

| Column | Type | Notes |
| --- | --- | --- |
| id | text primary key | Stable task id |
| title | text | |
| type | text | research_scan/project_review/memory_update/task_decomposition/weekly_report |
| project_id | text nullable | |
| owner_agent_id | text | references agents(id) |
| status | text | created/queued/running/waiting_approval/blocked/completed/failed/cancelled |
| priority | text | low/medium/high/critical |
| input_json | jsonb | |
| output_json | jsonb | |
| created_by | text | manual/schedule/agent |
| created_at | timestamptz | |
| updated_at | timestamptz | |

## agent_runs

| Column | Type | Notes |
| --- | --- | --- |
| id | text primary key | |
| agent_id | text | references agents(id) |
| task_id | text | references tasks(id) |
| status | text | running/completed/failed/cancelled |
| input_json | jsonb | |
| output_json | jsonb | |
| started_at | timestamptz | |
| ended_at | timestamptz nullable | |
| error_message | text nullable | |
| cost | numeric nullable | |

## tool_calls

| Column | Type | Notes |
| --- | --- | --- |
| id | text primary key | |
| run_id | text | references agent_runs(id) |
| tool_id | text | |
| input_json | jsonb | Redact secrets before storage |
| output_json | jsonb | |
| status | text | started/completed/failed/skipped |
| risk_level | text | low/medium/high/critical |
| created_at | timestamptz | |

## memory_items

| Column | Type | Notes |
| --- | --- | --- |
| id | text primary key | |
| type | text | knowledge/experience/skill |
| title | text | |
| content | text | |
| summary | text | |
| source_task_id | text nullable | references tasks(id) |
| source_run_id | text nullable | references agent_runs(id) |
| status | text | candidate/approved/active/deprecated/rejected/conflict |
| confidence | numeric | 0 to 1 |
| tags | text[] | |
| created_at | timestamptz | |
| updated_at | timestamptz | |

## skills

| Column | Type | Notes |
| --- | --- | --- |
| id | text primary key | |
| name | text | |
| description | text | |
| trigger_condition | text | |
| steps_json | jsonb | |
| tools_json | jsonb | |
| version | text | |
| status | text | candidate/active/deprecated |
| created_from_task_id | text nullable | references tasks(id) |
| created_at | timestamptz | |
| updated_at | timestamptz | |

## approvals

| Column | Type | Notes |
| --- | --- | --- |
| id | text primary key | |
| requesting_agent_id | text | references agents(id) |
| task_id | text nullable | references tasks(id) |
| action_type | text | |
| risk_level | text | low/medium/high/critical |
| summary | text | |
| details_json | jsonb | |
| status | text | pending/approved/rejected/needs_revision/expired |
| user_decision | text nullable | |
| created_at | timestamptz | |
| decided_at | timestamptz nullable | |

## schedules

| Column | Type | Notes |
| --- | --- | --- |
| id | text primary key | |
| agent_id | text | references agents(id) |
| task_type | text | |
| cron | text | |
| input_json | jsonb | |
| enabled | boolean | |
| last_run_at | timestamptz nullable | |
| next_run_at | timestamptz nullable | |
