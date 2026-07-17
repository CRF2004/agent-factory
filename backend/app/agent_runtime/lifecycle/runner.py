from __future__ import annotations

import logging
from threading import Event, Thread

from app.agent_runtime.lifecycle.heartbeat import HeartbeatService

logger = logging.getLogger(__name__)


class HeartbeatRunner:
    def __init__(self, service: HeartbeatService, poll_seconds: int = 30) -> None:
        self.service = service
        self.poll_seconds = max(1, poll_seconds)
        self._stop_event = Event()
        self._thread: Thread | None = None

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        if self.running:
            return
        self._stop_event.clear()
        self._thread = Thread(
            target=self._run,
            name="agent-heartbeat-runner",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=self.poll_seconds + 1)
        self._thread = None

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                self.service.run_due_agents()
            except Exception:
                logger.exception("Heartbeat polling cycle failed")
            self._stop_event.wait(self.poll_seconds)
