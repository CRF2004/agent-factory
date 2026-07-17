from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.agent_runtime.lifecycle.heartbeat import HeartbeatService
from app.api.deps import (
    get_heartbeat_service,
    get_repository,
    get_runtime_service,
)
from app.schemas.agent_spec import AgentSpec
from app.schemas.approval import ApprovalRequest
from app.schemas.heartbeat import (
    AgentHeartbeatState,
    HeartbeatRunResult,
    RunDueHeartbeatsResult,
)
from app.schemas.memory import MemoryItem
from app.schemas.run import AgentRun, ToolCall
from app.schemas.task import TaskSpec
from app.schemas.tool import ToolSpec
from app.services.repository import DuplicateError, NotFoundError, Repository
from app.services.runtime import RuntimeService, TaskNotRunnableError

router = APIRouter()


def map_error(exc: Exception) -> HTTPException:
    if isinstance(exc, NotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, DuplicateError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(exc, TaskNotRunnableError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# ── agents ───────────────────────────────────────────

@router.post("/agents", response_model=AgentSpec, status_code=status.HTTP_201_CREATED)
def create_agent(
    agent: AgentSpec, repository: Repository = Depends(get_repository)
) -> AgentSpec:
    try:
        return repository.create_agent(agent)
    except Exception as exc:
        raise map_error(exc) from exc


@router.get("/agents", response_model=list[AgentSpec])
def list_agents(repository: Repository = Depends(get_repository)) -> list[AgentSpec]:
    return repository.list_agents()


@router.post(
    "/agents/heartbeat/run-due",
    response_model=RunDueHeartbeatsResult,
)
def run_due_heartbeats(
    service: HeartbeatService = Depends(get_heartbeat_service),
) -> RunDueHeartbeatsResult:
    try:
        return service.run_due_agents()
    except Exception as exc:
        raise map_error(exc) from exc


@router.get(
    "/agents/{agent_id}/heartbeat",
    response_model=AgentHeartbeatState,
)
def get_agent_heartbeat(
    agent_id: str,
    service: HeartbeatService = Depends(get_heartbeat_service),
) -> AgentHeartbeatState:
    try:
        return service.get_state(agent_id)
    except Exception as exc:
        raise map_error(exc) from exc


@router.post(
    "/agents/{agent_id}/heartbeat",
    response_model=HeartbeatRunResult,
)
def run_agent_heartbeat(
    agent_id: str,
    force: bool = False,
    service: HeartbeatService = Depends(get_heartbeat_service),
) -> HeartbeatRunResult:
    try:
        return service.run_agent(agent_id, force=force)
    except Exception as exc:
        raise map_error(exc) from exc


@router.get("/agents/{agent_id}", response_model=AgentSpec)
def get_agent(
    agent_id: str, repository: Repository = Depends(get_repository)
) -> AgentSpec:
    try:
        return repository.get_agent(agent_id)
    except Exception as exc:
        raise map_error(exc) from exc


# ── tasks ────────────────────────────────────────────

@router.post("/tasks", response_model=TaskSpec, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskSpec, repository: Repository = Depends(get_repository)
) -> TaskSpec:
    try:
        repository.get_agent(task.owner_agent)
        return repository.create_task(task)
    except Exception as exc:
        raise map_error(exc) from exc


@router.get("/tasks", response_model=list[TaskSpec])
def list_tasks(repository: Repository = Depends(get_repository)) -> list[TaskSpec]:
    return repository.list_tasks()


@router.get("/tasks/{task_id}", response_model=TaskSpec)
def get_task(
    task_id: str, repository: Repository = Depends(get_repository)
) -> TaskSpec:
    try:
        return repository.get_task(task_id)
    except Exception as exc:
        raise map_error(exc) from exc


@router.post("/tasks/{task_id}/run", response_model=AgentRun)
def run_task(
    task_id: str, runtime: RuntimeService = Depends(get_runtime_service)
) -> AgentRun:
    try:
        return runtime.run_task(task_id)
    except Exception as exc:
        raise map_error(exc) from exc


# ── runs ─────────────────────────────────────────────

@router.get("/runs", response_model=list[AgentRun])
def list_runs(repository: Repository = Depends(get_repository)) -> list[AgentRun]:
    return repository.list_runs()


# ── tool calls ───────────────────────────────────────

@router.get("/tool-calls", response_model=list[ToolCall])
def list_tool_calls(
    repository: Repository = Depends(get_repository),
) -> list[ToolCall]:
    return repository.list_tool_calls()


# ── memory items ─────────────────────────────────────

@router.get("/memory-items", response_model=list[MemoryItem])
def list_memory_items(
    repository: Repository = Depends(get_repository),
) -> list[MemoryItem]:
    return repository.list_memory_items()


# ── approvals ────────────────────────────────────────

@router.get("/approvals", response_model=list[ApprovalRequest])
def list_approvals(
    repository: Repository = Depends(get_repository),
) -> list[ApprovalRequest]:
    return repository.list_approvals()


@router.post("/approvals/{approval_id}/approve", response_model=ApprovalRequest)
def approve(
    approval_id: str, repository: Repository = Depends(get_repository)
) -> ApprovalRequest:
    try:
        approval = repository.get_approval(approval_id)
        approval.status = "approved"
        repository.upsert_approval(approval)
        return approval
    except Exception as exc:
        raise map_error(exc) from exc


@router.post("/approvals/{approval_id}/reject", response_model=ApprovalRequest)
def reject(
    approval_id: str, repository: Repository = Depends(get_repository)
) -> ApprovalRequest:
    try:
        approval = repository.get_approval(approval_id)
        approval.status = "rejected"
        repository.upsert_approval(approval)
        return approval
    except Exception as exc:
        raise map_error(exc) from exc


# ── tools ───────────────────────────────────────────

@router.post("/tools", response_model=ToolSpec, status_code=status.HTTP_201_CREATED)
def register_tool(
    tool: ToolSpec, repository: Repository = Depends(get_repository)
) -> ToolSpec:
    try:
        return repository.register_tool(tool)
    except Exception as exc:
        raise map_error(exc) from exc


@router.get("/tools", response_model=list[ToolSpec])
def list_tools(repository: Repository = Depends(get_repository)) -> list[ToolSpec]:
    return repository.list_tools()


@router.get("/tools/{tool_id}", response_model=ToolSpec)
def get_tool(
    tool_id: str, repository: Repository = Depends(get_repository)
) -> ToolSpec:
    try:
        return repository.get_tool(tool_id)
    except Exception as exc:
        raise map_error(exc) from exc
