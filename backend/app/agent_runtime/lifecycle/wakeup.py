from ..brain import AgentBrain
from ..models import AgentSpec


class AgentWakeup:
    def __init__(self, brain: AgentBrain | None = None):
        self.brain = brain or AgentBrain()

    def run_once(self, agent: AgentSpec, context: dict):
        """Wake an agent and ask it whether new work is needed."""
        return self.brain.decide(agent, context)
