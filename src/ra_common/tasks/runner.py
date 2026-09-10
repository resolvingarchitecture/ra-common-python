"""Ports ``ra.common.tasks.TaskRunner``.

The Java version drove a ``ThreadPoolExecutor`` + ``ScheduledThreadPoolExecutor``
from a 30-second poll loop. This port keeps the poll loop but gives every task
its own thread. A task whose ``periodicity_ms`` is ``-1`` is skipped; ``0`` runs
once; ``> 0`` re-runs on a fixed delay.
"""

from __future__ import annotations

import threading
from enum import Enum

from .task import Task, TaskStatus


class RunnerStatus(str, Enum):
    RUNNING = "Running"
    STOPPING = "Stopping"
    SHUTDOWN = "Shutdown"


class _Managed:
    def __init__(self, task: Task) -> None:
        self.task = task
        self.status = TaskStatus.READY
        self.stop = threading.Event()
        self.worker: threading.Thread | None = None
        self.scheduled = False


class TaskRunner:
    """Schedules and runs :class:`Task` objects on background threads."""

    def __init__(self, poll_period_ms: int = 30_000) -> None:
        self._tasks: list[_Managed] = []
        self._lock = threading.Lock()
        self._wake = threading.Condition(self._lock)
        self._running = False
        self._poll_ms = max(1, poll_period_ms)
        self._runner: threading.Thread | None = None

    def set_poll_period_ms(self, ms: int) -> None:
        with self._wake:
            self._poll_ms = max(1, ms)
            self._wake.notify_all()

    def add_task(self, task: Task) -> None:
        with self._wake:
            self._tasks.append(_Managed(task))
            self._wake.notify_all()

    def poke(self) -> None:
        with self._wake:
            self._wake.notify_all()

    def start(self) -> None:
        if self._runner is not None:
            return
        self._running = True
        self._runner = threading.Thread(target=self._run_loop, name="task-runner", daemon=True)
        self._runner.start()

    def status(self) -> RunnerStatus:
        if self._runner is None:
            return RunnerStatus.SHUTDOWN
        return RunnerStatus.RUNNING if self._running else RunnerStatus.STOPPING

    def task_count(self) -> int:
        with self._lock:
            return len(self._tasks)

    def shutdown(self) -> None:
        with self._wake:
            self._running = False
            for m in self._tasks:
                m.stop.set()
            self._wake.notify_all()
        if self._runner is not None:
            self._runner.join()
            self._runner = None
        with self._lock:
            for m in self._tasks:
                if m.worker is not None:
                    m.worker.join()
            self._tasks.clear()

    def _run_loop(self) -> None:
        while self._running:
            with self._wake:
                self._tasks = [m for m in self._tasks if not self._reap(m)]
                for m in self._tasks:
                    if m.scheduled:
                        continue
                    cfg = m.task.config()
                    if cfg.periodicity_ms == -1:
                        continue
                    m.scheduled = True
                    m.worker = threading.Thread(
                        target=self._worker, args=(m, cfg), name=f"task-{cfg.name}", daemon=True
                    )
                    m.worker.start()
                self._wake.wait(self._poll_ms / 1000.0)

    @staticmethod
    def _reap(m: _Managed) -> bool:
        if m.status == TaskStatus.COMPLETED:
            if m.worker is not None:
                m.worker.join()
            return True
        return False

    @staticmethod
    def _worker(m: _Managed, cfg) -> None:  # noqa: ANN001
        if cfg.delayed and cfg.delay_ms > 0:
            if m.stop.wait(cfg.delay_ms / 1000.0):
                m.status = TaskStatus.COMPLETED
                m.task.on_stop()
                return
        while True:
            if m.stop.is_set() or m.task.should_stop():
                m.task.on_stop()
                break
            m.status = TaskStatus.RUNNING
            m.task.execute()
            if cfg.periodicity_ms <= 0:
                break
            m.status = TaskStatus.READY
            if m.stop.wait(cfg.periodicity_ms / 1000.0):
                m.task.on_stop()
                break
        m.status = TaskStatus.COMPLETED
