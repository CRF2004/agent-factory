from .models import AgentSpec, AgentTask


class AgentBrain:
    """Minimal decision layer for autonomous agents."""

    def decide(self, agent: AgentSpec, context: dict) -> AgentTask | None:
        if not agent.goals:
            return None

        if context.get("needs_attention"):
            return AgentTask(
                task_type="agent_review",
                description=context.get("reason", "Review current state"),
                priority="high",
            )

        return AgentTask(
            task_type="proactive_check",
            description=f"Advance goal: {agent.goals[0]}",
            priority="normal",
        )
