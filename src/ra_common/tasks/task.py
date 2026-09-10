"""Ports ``ra.common.tasks.{Task, BaseTask}``."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class TaskStatus(str, Enum):
    READY = "Ready"
    RUNNING = "Running"
    COMPLETED = "Completed"


@dataclass
class TaskConfig:
    """Scheduling configuration for a :class:`Task`. Ports the ``BaseTask`` flags.

    ``periodicity_ms``: ``0`` runs once; ``> 0`` re-runs every N milliseconds;
    ``-1`` is disabled.
    """

    name: str
    periodicity_ms: int = 0
    delayed: bool = False
    delay_ms: int = 0
    fixed_delay: bool = False
    long_running: bool = False

    @classmethod
    def once(cls, name: str) -> "TaskConfig":
        return cls(name=name)

    @classmethod
    def periodic(cls, name: str, period_ms: int) -> "TaskConfig":
        return cls(name=name, periodicity_ms=period_ms)

    def with_delay(self, delay_ms: int) -> "TaskConfig":
        self.delayed = True
        self.delay_ms = delay_ms
        return self


class Task(ABC):
    """A unit of work run by a :class:`~ra_common.tasks.TaskRunner`."""

    @abstractmethod
    def config(self) -> TaskConfig: ...

    @abstractmethod
    def execute(self) -> bool:
        """Do the work. Return ``True`` on success."""

    def should_stop(self) -> bool:
        return False

    def on_stop(self) -> None:
        pass
