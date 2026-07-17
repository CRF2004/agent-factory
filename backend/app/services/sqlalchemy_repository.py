from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.tables import (
    AgentHeartbeatRecord,
    AgentRecord,
    AgentRunRecord,
    ApprovalRecord,
    MemoryItemRecord,
    TaskRecord,
    ToolCallRecord,
)
from app.schemas.agent_spec import AgentSpec
from app.schemas.approval import ApprovalRequest
from app.schemas.heartbeat import AgentHeartbeatState
from app.schemas.memory import MemoryItem
from app.schemas.run import AgentRun, ToolCall
from app.schemas.task import TaskSpec
from app.services.repository import DuplicateError, NotFoundError

T = TypeVar("T")


class SQLAlchemyRepository:
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self.session_factory = session_factory

    def create_agent(self, agent: AgentSpec) -> AgentSpec:
        with self.session_factory() as session:
            if session.get(AgentRecord, agent.agent_id):
                raise DuplicateError(f"agent already exists: {agent.agent_id}")
            session.add(self._agent_to_record(agent))
            self._commit(session)
        return agent

    def list_agents(self) -> list[AgentSpec]:
        with self.session_factory() as session:
            records = session.scalars(select(AgentRecord)).all()
            return [AgentSpec.model_validate(record.spec_json) for record in records]

    def get_agent(self, agent_id: str) -> AgentSpec:
        with self.session_factory() as session:
            record = session.get(AgentRecord, agent_id)
            if record is None:
                raise NotFoundError(agent_id)
            return AgentSpec.model_validate(record.spec_json)

    def upsert_agent(self, agent: AgentSpec) -> AgentSpec:
        with self.session_factory() as session:
            session.merge(self._agent_to_record(agent))
            self._commit(session)
        return agent

    def create_task(self, task: TaskSpec) -> TaskSpec:
        with self.session_factory() as session:
            if session.get(TaskRecord, task.task_id):
                raise DuplicateError(f"task already exists: {task.task_id}")
            session.add(self._task_to_record(task))
            self._commit(session)
        return task

    def list_tasks(self) -> list[TaskSpec]:
        with self.session_factory() as session:
            records = session.scalars(select(TaskRecord)).all()
            return [TaskSpec.model_validate(record.spec_json) for record in records]

    def get_task(self, task_id: str) -> TaskSpec:
        with self.session_factory() as session:
            record = session.get(TaskRecord, task_id)
            if record is None:
                raise NotFoundError(task_id)
            return TaskSpec.model_validate(record.spec_json)

    def upsert_task(self, task: TaskSpec) -> TaskSpec:
        with self.session_factory() as session:
            session.merge(self._task_to_record(task))
            self._commit(session)
        return task

    def create_run(self, run: AgentRun) -> AgentRun:
        with self.session_factory() as session:
            session.add(self._run_to_record(run))
            self._commit(session)
        return run

    def list_runs(self) -> list[AgentRun]:
        with self.session_factory() as session:
            records = session.scalars(select(AgentRunRecord)).all()
            return [AgentRun.model_validate(record.spec_json) for record in records]

    def upsert_run(self, run: AgentRun) -> AgentRun:
        with self.session_factory() as session:
            session.merge(self._run_to_record(run))
            self._commit(session)
        return run

    def create_tool_call(self, tool_call: ToolCall) -> ToolCall:
        with self.session_factory() as session:
            session.add(self._tool_call_to_record(tool_call))
            self._commit(session)
        return tool_call

    def list_tool_calls(self) -> list[ToolCall]:
        with self.session_factory() as session:
            records = session.scalars(select(ToolCallRecord)).all()
            return [ToolCall.model_validate(record.spec_json) for record in records]

    def create_memory_item(self, memory_item: MemoryItem) -> MemoryItem:
        with self.session_factory() as session:
            if session.get(MemoryItemRecord, memory_item.id):
                raise DuplicateError(f"memory item already exists: {memory_item.id}")
            session.add(self._memory_item_to_record(memory_item))
            self._commit(session)
        return memory_item

    def list_memory_items(self) -> list[MemoryItem]:
        with self.session_factory() as session:
            records = session.scalars(select(MemoryItemRecord)).all()
            return [MemoryItem.model_validate(record.spec_json) for record in records]

    def upsert_memory_item(self, memory_item: MemoryItem) -> MemoryItem:
        with self.session_factory() as session:
            session.merge(self._memory_item_to_record(memory_item))
            self._commit(session)
        return memory_item

    def get_heartbeat_state(self, agent_id: str) -> AgentHeartbeatState:
        with self.session_factory() as session:
            record = session.get(AgentHeartbeatRecord, agent_id)
            if record is None:
                raise NotFoundError(agent_id)
            return AgentHeartbeatState.model_validate(record.state_json)

    def upsert_heartbeat_state(
        self, state: AgentHeartbeatState
    ) -> AgentHeartbeatState:
        with self.session_factory() as session:
            session.merge(self._heartbeat_to_record(state))
            self._commit(session)
        return state

    def acquire_heartbeat_lease(
        self,
        agent_id: str,
        lease_token: str,
        now: str,
        lease_until: str,
    ) -> AgentHeartbeatState | None:
        with self.session_factory() as session:
            record = session.get(
                AgentHeartbeatRecord,
                agent_id,
                with_for_update=True,
            )
            if record is None:
                state = AgentHeartbeatState(
                    agent_id=agent_id,
                    lease_token=lease_token,
                    lease_until=lease_until,
                )
                session.add(self._heartbeat_to_record(state))
            else:
                state = AgentHeartbeatState.model_validate(record.state_json)
                if state.lease_until and _is_after(state.lease_until, now):
                    session.rollback()
                    return None
                state.lease_token = lease_token
                state.lease_until = lease_until
                session.merge(self._heartbeat_to_record(state))
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                return None
            return state

    def list_approvals(self) -> list[ApprovalRequest]:
        with self.session_factory() as session:
            records = session.scalars(select(ApprovalRecord)).all()
            return [ApprovalRequest.model_validate(record.spec_json) for record in records]

    def create_approval(self, approval: ApprovalRequest) -> ApprovalRequest:
        with self.session_factory() as session:
            if session.get(ApprovalRecord, approval.approval_id):
                raise DuplicateError(f"approval already exists: {approval.approval_id}")
            session.add(self._approval_to_record(approval))
            self._commit(session)
        return approval

    def get_approval(self, approval_id: str) -> ApprovalRequest:
        with self.session_factory() as session:
            record = session.get(ApprovalRecord, approval_id)
            if record is None:
                raise NotFoundError(approval_id)
            return ApprovalRequest.model_validate(record.spec_json)

    def upsert_approval(self, approval: ApprovalRequest) -> ApprovalRequest:
        with self.session_factory() as session:
            session.merge(self._approval_to_record(approval))
            self._commit(session)
        return approval

    def _commit(self, session: Session) -> None:
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise DuplicateError(str(exc)) from exc

    def _agent_to_record(self, agent: AgentSpec) -> AgentRecord:
        payload = agent.model_dump(mode="json")
        return AgentRecord(
            id=agent.agent_id,
            name=agent.name,
            role=agent.role,
            mission=agent.mission,
            status=agent.status.value,
            autonomy_level=agent.autonomy_level.value,
            spec_json=payload,
        )

    def _heartbeat_to_record(
        self, state: AgentHeartbeatState
    ) -> AgentHeartbeatRecord:
        return AgentHeartbeatRecord(
            agent_id=state.agent_id,
            next_wakeup_at=state.next_wakeup_at,
            lease_token=state.lease_token,
            lease_until=state.lease_until,
            state_json=state.model_dump(mode="json"),
        )

    def _task_to_record(self, task: TaskSpec) -> TaskRecord:
        payload = task.model_dump(mode="json")
        return TaskRecord(
            id=task.task_id,
            title=task.title,
            type=task.type.value,
            project_id=task.project_id,
            owner_agent_id=task.owner_agent,
            status=task.status.value,
            priority=task.priority.value,
            input_json=task.input,
            output_json=task.output,
            created_by=task.created_by,
            spec_json=payload,
        )

    def _run_to_record(self, run: AgentRun) -> AgentRunRecord:
        payload = run.model_dump(mode="json")
        return AgentRunRecord(
            id=run.id,
            agent_id=run.agent_id,
            task_id=run.task_id,
            status=run.status.value,
            input_json=run.input,
            output_json=run.output,
            started_at=run.started_at,
            ended_at=run.ended_at,
            error_message=run.error_message,
            cost=run.cost,
            spec_json=payload,
        )

    def _tool_call_to_record(self, tool_call: ToolCall) -> ToolCallRecord:
        payload = tool_call.model_dump(mode="json")
        return ToolCallRecord(
            id=tool_call.id,
            run_id=tool_call.run_id,
            tool_id=tool_call.tool_id,
            input_json=tool_call.input,
            output_json=tool_call.output,
            status=tool_call.status.value,
            risk_level=tool_call.risk_level.value,
            spec_json=payload,
        )

    def _memory_item_to_record(self, memory_item: MemoryItem) -> MemoryItemRecord:
        payload = memory_item.model_dump(mode="json")
        return MemoryItemRecord(
            id=memory_item.id,
            type=memory_item.type.value,
            title=memory_item.title,
            content=memory_item.content,
            summary=memory_item.summary,
            source_task_id=memory_item.source_task_id,
            source_run_id=memory_item.source_run_id,
            status=memory_item.status.value,
            confidence=memory_item.confidence,
            spec_json=payload,
        )

    def _approval_to_record(self, approval: ApprovalRequest) -> ApprovalRecord:
        payload = approval.model_dump(mode="json")
        return ApprovalRecord(
            id=approval.approval_id,
            requesting_agent_id=approval.requesting_agent,
            task_id=approval.task_id,
            action_type=approval.action_type,
            risk_level=approval.risk_level.value,
            summary=approval.summary,
            details_json=approval.details,
            status=approval.status.value,
            spec_json=payload,
        )


def _is_after(value: str, reference: str) -> bool:
    return datetime.fromisoformat(value) > datetime.fromisoformat(reference)
