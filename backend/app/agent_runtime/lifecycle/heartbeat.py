import asyncio
from datetime import datetime


class AgentHeartbeat:
    """Lightweight heartbeat scheduler for resident agents."""

    def __init__(self, agent, interval_seconds: int = 300):
        self.agent = agent
        self.interval_seconds = interval_seconds
        self.running = False

    async def start(self):
        self.running = True
        while self.running:
            await self.tick()
            await asyncio.sleep(self.interval_seconds)

    async def tick(self):
        context = {
            "timestamp": datetime.utcnow().isoformat(),
            "needs_attention": False,
        }
        return await self.agent.wake_up(context)

    def stop(self):
        self.running = False
