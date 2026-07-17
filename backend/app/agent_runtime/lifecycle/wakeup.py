from __future__ import annotations

from app.agent_runtime.cognition.planner import Planner


class WakeupLoop:
    """Heartbeat entrypoint for resident agents."""

    def __init__(self, planner: Planner | None = None) -> None:
        self.planner = planner or Planner()

    def observe_and_plan(self, agent, recent_tasks=None, recent_memory=None):
        observation = {
            "active_tasks": recent_tasks or [],
            "recent_memory": recent_memory or [],
        }
        return self.planner.create_plan(agent, observation)
