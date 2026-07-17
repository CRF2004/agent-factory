from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.agent_runtime.runtime import AutonomousRuntime
from app.schemas.agent_spec import AgentStatus
from app.schemas.heartbeat import (
    AgentHeartbeatState,
    HeartbeatAction,
    HeartbeatRunResult,
    RunDueHeartbeatsResult,
)
from app.services.repository import NotFoundError, Repository


class HeartbeatService:
    def __init__(
        self,
        repository: Repository,
        autonomous_runtime: AutonomousRuntime,
        default_wakeup_seconds: int = 3600,
        lease_seconds: int = 300,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.repository = repository
        self.autonomous_runtime = autonomous_runtime
        self.default_wakeup_seconds = max(1, default_wakeup_seconds)
        self.lease_seconds = max(1, lease_seconds)
        self.clock = clock or (lambda: datetime.now(UTC))

    def get_state(self, agent_id: str) -> AgentHeartbeatState:
        self.repository.get_agent(agent_id)
        return self._load_state(agent_id)

    def run_agent(self, agent_id: str, force: bool = False) -> HeartbeatRunResult:
        agent = self.repository.get_agent(agent_id)
        now = self._now()
        state = self._load_state(agent_id)

        if agent.status == AgentStatus.disabled:
            state.next_wakeup_at = None
            state.lease_token = None
            state.lease_until = None
            state = self.repository.upsert_heartbeat_state(state)
            return HeartbeatRunResult(
                agent_id=agent_id,
                action=HeartbeatAction.disabled,
                reason="agent disabled",
                state=state,
            )

        if not force and state.next_wakeup_at and _parse(state.next_wakeup_at) > now:
            return HeartbeatRunResult(
                agent_id=agent_id,
                action=HeartbeatAction.no_action,
                reason="mission handled within cooldown",
                state=state,
            )

        lease_token = f"lease_{uuid4().hex}"
        lease_until = now + timedelta(seconds=self.lease_seconds)
        leased_state = self.repository.acquire_heartbeat_lease(
            agent_id=agent_id,
            lease_token=lease_token,
            now=_iso(now),
            lease_until=_iso(lease_until),
        )
        if leased_state is None:
            return HeartbeatRunResult(
                agent_id=agent_id,
                action=HeartbeatAction.already_running,
                reason="heartbeat lease already held",
                state=self._load_state(agent_id),
            )

        state = leased_state
        state.last_wakeup_at = _iso(now)
        state.last_error = None
        self.repository.upsert_heartbeat_state(state)

        try:
            cycle = self.autonomous_runtime.run_once(agent_id)
            wakeup_seconds = max(1, cycle.next_wakeup_seconds)
            state.next_wakeup_at = _iso(now + timedelta(seconds=wakeup_seconds))
            state.consecutive_failures = 0
            state.last_error = None

            if cycle.acted and cycle.executed_task is not None:
                state.last_action_at = _iso(now)
                state.last_task_id = cycle.executed_task.task_id
                action = HeartbeatAction.task_created
            else:
                action = HeartbeatAction.no_action

            state.lease_token = None
            state.lease_until = None
            state = self.repository.upsert_heartbeat_state(state)
            return HeartbeatRunResult(
                agent_id=agent_id,
                action=action,
                reason=cycle.decision_reason,
                state=state,
                task=cycle.executed_task,
                run=cycle.run,
                experience_memory=cycle.experience_memory,
            )
        except Exception as exc:
            state.consecutive_failures += 1
            state.last_error = str(exc)
            retry_seconds = min(
                self.default_wakeup_seconds,
                60 * (2 ** min(state.consecutive_failures - 1, 6)),
            )
            state.next_wakeup_at = _iso(now + timedelta(seconds=retry_seconds))
            state.lease_token = None
            state.lease_until = None
            state = self.repository.upsert_heartbeat_state(state)
            return HeartbeatRunResult(
                agent_id=agent_id,
                action=HeartbeatAction.error,
                reason=str(exc),
                state=state,
            )

    def run_due_agents(self) -> RunDueHeartbeatsResult:
        agents = self.repository.list_agents()
        now = self._now()
        results: list[HeartbeatRunResult] = []
        due_agents = 0

        for agent in agents:
            if agent.status == AgentStatus.disabled:
                continue
            state = self._load_state(agent.agent_id)
            if state.next_wakeup_at and _parse(state.next_wakeup_at) > now:
                continue
            due_agents += 1
            results.append(self.run_agent(agent.agent_id))

        return RunDueHeartbeatsResult(
            checked_agents=len(agents),
            due_agents=due_agents,
            results=results,
        )

    def _load_state(self, agent_id: str) -> AgentHeartbeatState:
        try:
            return self.repository.get_heartbeat_state(agent_id)
        except NotFoundError:
            state = AgentHeartbeatState(agent_id=agent_id)
            return self.repository.upsert_heartbeat_state(state)

    def _now(self) -> datetime:
        value = self.clock()
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)


def _iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat()


def _parse(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
