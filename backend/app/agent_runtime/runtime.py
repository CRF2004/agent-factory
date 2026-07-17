from .brain import AgentBrain
from .models import AgentSpec, AgentTask


class AgentRuntime:
    """Runtime wrapper for long-running autonomous agents."""

    def __init__(self, spec: AgentSpec):
        self.spec = spec
        self.brain = AgentBrain()
        self.status = "idle"
        self.tasks: list[AgentTask] = []

    async def wake_up(self, context: dict):
        self.status = "running"
        task = self.brain.decide(self.spec, context)

        if task:
            self.tasks.append(task)

        self.status = "idle"
        return task
