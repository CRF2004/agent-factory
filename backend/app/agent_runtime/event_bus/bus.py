from collections import defaultdict
from typing import Callable

from .events import AgentEvent


class EventBus:
    """Simple synchronous event bus.

    Designed as an interface that can later be replaced by Redis/NATS.
    """

    def __init__(self):
        self.handlers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Callable):
        self.handlers[event_type].append(handler)

    def publish(self, event: AgentEvent):
        for handler in self.handlers.get(event.event_type, []):
            handler(event)
