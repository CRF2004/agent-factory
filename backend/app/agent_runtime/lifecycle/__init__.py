from __future__ import annotations

from typing import Any

__all__ = ["HeartbeatRunner", "HeartbeatService", "WakeupLoop"]


def __getattr__(name: str) -> Any:
    if name == "HeartbeatRunner":
        from app.agent_runtime.lifecycle.runner import HeartbeatRunner

        return HeartbeatRunner
    if name == "HeartbeatService":
        from app.agent_runtime.lifecycle.heartbeat import HeartbeatService

        return HeartbeatService
    if name == "WakeupLoop":
        from app.agent_runtime.lifecycle.wakeup import WakeupLoop

        return WakeupLoop
    raise AttributeError(name)
