from __future__ import annotations

from copy import deepcopy
from typing import Protocol

from app.schemas.agent_spec import AgentSpec
from app.schemas.approval import ApprovalRequest
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
        self.approvals: dict[str, ApprovalRequest] = {}
        self.tools: dict[str, ToolSpec] = {}

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
        self.memory_items[memory_item.id] = deepcopy(memory_item)
        return deepcopy(memory_item)

    def list_memory_items(self) -> list[MemoryItem]:
        return [deepcopy(item) for item in self.memory_items.values()]

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
