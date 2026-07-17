from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from threading import RLock
from typing import Protocol

from app.schemas.agent_spec import AgentSpec
from app.schemas.approval import ApprovalRequest
from app.schemas.heartbeat import AgentHeartbeatState
from app.schemas.memory import MemoryItem
from app.schemas.run import AgentRun, ToolCall
from app.schemas.task import TaskSpec
from app.schemas.tool import ToolSpec


class NotFoundError(KeyError):
    pass


class DuplicateError(ValueError):
    pass


class Repository(Protocol):
    # agents
    def create_agent(self, agent: AgentSpec) -> AgentSpec: ...
    def list_agents(self) -> list[AgentSpec]: ...
    def get_agent(self, agent_id: str) -> AgentSpec: ...
    def upsert_agent(self, agent: AgentSpec) -> AgentSpec: ...

    # tasks
    def create_task(self, task: TaskSpec) -> TaskSpec: ...
    def list_tasks(self) -> list[TaskSpec]: ...
    def get_task(self, task_id: str) -> TaskSpec: ...
    def upsert_task(self, task: TaskSpec) -> TaskSpec: ...

    # runs
    def create_run(self, run: AgentRun) -> AgentRun: ...
    def list_runs(self) -> list[AgentRun]: ...
    def upsert_run(self, run: AgentRun) -> AgentRun: ...

    # tool calls
    def create_tool_call(self, tool_call: ToolCall) -> ToolCall: ...
    def list_tool_calls(self) -> list[ToolCall]: ...

    # memory
    def create_memory_item(self, memory_item: MemoryItem) -> MemoryItem: ...
    def list_memory_items(self) -> list[MemoryItem]: ...
    def upsert_memory_item(self, memory_item: MemoryItem) -> MemoryItem: ...

    # heartbeat
    def get_heartbeat_state(self, agent_id: str) -> AgentHeartbeatState: ...
    def upsert_heartbeat_state(
        self, state: AgentHeartbeatState
    ) -> AgentHeartbeatState: ...
    def acquire_heartbeat_lease(
        self,
        agent_id: str,
        lease_token: str,
        now: str,
        lease_until: str,
    ) -> AgentHeartbeatState | None: ...

    # approvals
    def create_approval(self, approval: ApprovalRequest) -> ApprovalRequest: ...
    def list_approvals(self) -> list[ApprovalRequest]: ...
    def get_approval(self, approval_id: str) -> ApprovalRequest: ...
    def upsert_approval(self, approval: ApprovalRequest) -> ApprovalRequest: ...

    # tools
    def register_tool(self, tool: ToolSpec) -> ToolSpec: ...
    def get_tool(self, tool_id: str) -> ToolSpec: ...
    def list_tools(self) -> list[ToolSpec]: ...


class InMemoryRepository:
    def __init__(self) -> None:
        self.agents: dict[str, AgentSpec] = {}
        self.tasks: dict[str, TaskSpec] = {}
        self.agent_runs: dict[str, AgentRun] = {}
        self.tool_calls: dict[str, ToolCall] = {}
        self.memory_items: dict[str, MemoryItem] = {}
        self.heartbeat_states: dict[str, AgentHeartbeatState] = {}
        self.approvals: dict[str, ApprovalRequest] = {}
        self.tools: dict[str, ToolSpec] = {}
        self._heartbeat_lock = RLock()

    # ── agents ──────────────────────────────────────

    def create_agent(self, agent: AgentSpec) -> AgentSpec:
        if agent.agent_id in self.agents:
            raise DuplicateError(f"agent already exists: {agent.agent_id}")
        self.agents[agent.agent_id] = deepcopy(agent)
        return deepcopy(agent)

    def list_agents(self) -> list[AgentSpec]:
        return [deepcopy(item) for item in self.agents.values()]

    def get_agent(self, agent_id: str) -> AgentSpec:
        if agent_id not in self.agents:
            raise NotFoundError(agent_id)
        return deepcopy(self.agents[agent_id])

    def upsert_agent(self, agent: AgentSpec) -> AgentSpec:
        self.agents[agent.agent_id] = deepcopy(agent)
        return deepcopy(agent)

    # ── tasks ───────────────────────────────────────

    def create_task(self, task: TaskSpec) -> TaskSpec:
        if task.task_id in self.tasks:
            raise DuplicateError(f"task already exists: {task.task_id}")
        self.tasks[task.task_id] = deepcopy(task)
        return deepcopy(task)

    def list_tasks(self) -> list[TaskSpec]:
        return [deepcopy(item) for item in self.tasks.values()]

    def get_task(self, task_id: str) -> TaskSpec:
        if task_id not in self.tasks:
            raise NotFoundError(task_id)
        return deepcopy(self.tasks[task_id])

    def upsert_task(self, task: TaskSpec) -> TaskSpec:
        self.tasks[task.task_id] = deepcopy(task)
        return deepcopy(task)

    # ── runs ────────────────────────────────────────

    def create_run(self, run: AgentRun) -> AgentRun:
        self.agent_runs[run.id] = deepcopy(run)
        return deepcopy(run)

    def list_runs(self) -> list[AgentRun]:
        return [deepcopy(item) for item in self.agent_runs.values()]

    def upsert_run(self, run: AgentRun) -> AgentRun:
        self.agent_runs[run.id] = deepcopy(run)
        return deepcopy(run)

    # ── tool calls ──────────────────────────────────

    def create_tool_call(self, tool_call: ToolCall) -> ToolCall:
        self.tool_calls[tool_call.id] = deepcopy(tool_call)
        return deepcopy(tool_call)

    def list_tool_calls(self) -> list[ToolCall]:
        return [deepcopy(item) for item in self.tool_calls.values()]

    # ── memory ──────────────────────────────────────

    def create_memory_item(self, memory_item: MemoryItem) -> MemoryItem:
        if memory_item.id in self.memory_items:
            raise DuplicateError(f"memory item already exists: {memory_item.id}")
        self.memory_items[memory_item.id] = deepcopy(memory_item)
        return deepcopy(memory_item)

    def list_memory_items(self) -> list[MemoryItem]:
        return [deepcopy(item) for item in self.memory_items.values()]

    def upsert_memory_item(self, memory_item: MemoryItem) -> MemoryItem:
        self.memory_items[memory_item.id] = deepcopy(memory_item)
        return deepcopy(memory_item)

    # ── heartbeat ───────────────────────────────────

    def get_heartbeat_state(self, agent_id: str) -> AgentHeartbeatState:
        with self._heartbeat_lock:
            if agent_id not in self.heartbeat_states:
                raise NotFoundError(agent_id)
            return deepcopy(self.heartbeat_states[agent_id])

    def upsert_heartbeat_state(
        self, state: AgentHeartbeatState
    ) -> AgentHeartbeatState:
        with self._heartbeat_lock:
            self.heartbeat_states[state.agent_id] = deepcopy(state)
            return deepcopy(state)

    def acquire_heartbeat_lease(
        self,
        agent_id: str,
        lease_token: str,
        now: str,
        lease_until: str,
    ) -> AgentHeartbeatState | None:
        with self._heartbeat_lock:
            state = deepcopy(
                self.heartbeat_states.get(
                    agent_id, AgentHeartbeatState(agent_id=agent_id)
                )
            )
            if state.lease_until and _is_after(state.lease_until, now):
                return None
            state.lease_token = lease_token
            state.lease_until = lease_until
            self.heartbeat_states[agent_id] = deepcopy(state)
            return state

    # ── approvals ───────────────────────────────────

    def create_approval(self, approval: ApprovalRequest) -> ApprovalRequest:
        if approval.approval_id in self.approvals:
            raise DuplicateError(f"approval already exists: {approval.approval_id}")
        self.approvals[approval.approval_id] = deepcopy(approval)
        return deepcopy(approval)

    def list_approvals(self) -> list[ApprovalRequest]:
        return [deepcopy(item) for item in self.approvals.values()]

    def get_approval(self, approval_id: str) -> ApprovalRequest:
        if approval_id not in self.approvals:
            raise NotFoundError(approval_id)
        return deepcopy(self.approvals[approval_id])

    def upsert_approval(self, approval: ApprovalRequest) -> ApprovalRequest:
        self.approvals[approval.approval_id] = deepcopy(approval)
        return deepcopy(approval)

    # ── tools ──────────────────────────────────────

    def register_tool(self, tool: ToolSpec) -> ToolSpec:
        if tool.tool_id in self.tools:
            raise DuplicateError(f"tool already registered: {tool.tool_id}")
        self.tools[tool.tool_id] = deepcopy(tool)
        return deepcopy(tool)

    def get_tool(self, tool_id: str) -> ToolSpec:
        if tool_id not in self.tools:
            raise NotFoundError(tool_id)
        return deepcopy(self.tools[tool_id])

    def list_tools(self) -> list[ToolSpec]:
        return [deepcopy(item) for item in self.tools.values()]


def _is_after(value: str, reference: str) -> bool:
    return datetime.fromisoformat(value) > datetime.fromisoformat(reference)
