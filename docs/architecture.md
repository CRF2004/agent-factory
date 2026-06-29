# Phase 0 Architecture

Agent Factory owns the core state:

- Agent Spec
- Task state
- Agent run state
- Tool call audit logs
- Memory state
- Approval state
- Schedule state

External frameworks are adapters. They may execute workflow steps, but they must not be the source of truth for long-term state.

## MVP Runtime Boundary

```text
Agent Spec
  -> Task
  -> Agent Run
  -> Tool Calls
  -> Output
  -> Candidate Memory / Follow-up Task / Approval
```

## Phase 0 Deliverables

- JSON Schemas for persisted contracts.
- Pydantic models for backend validation.
- Built-in templates for the first three agents.
- Database design document.
