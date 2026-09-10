"""Lifecycle and status contracts shared by services and long-lived components.

Ports ``ra.common.LifeCycle``, ``ra.common.Status`` and ``ra.common.Client``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .envelope import Envelope


class Status(str, Enum):
    """Coarse run state of a component. Ports ``ra.common.Status``."""

    INITIALIZED = "Initialized"
    STARTING = "Starting"
    RUNNING = "Running"
    PAUSED = "Paused"
    STOPPING = "Stopping"
    STOPPED = "Stopped"
    ERRORED = "Errored"


class LifeCycle(ABC):
    """Start / pause / restart / shutdown contract. Ports ``ra.common.LifeCycle``.

    Every method returns ``True`` on success, matching the Java API. ``unpause``
    is named as such (rather than ``resume``) to mirror the Java note about the
    ``Thread.resume`` clash.
    """

    @abstractmethod
    def start(self, properties: dict[str, str]) -> bool:
        """Start the component with the given configuration."""

    def pause(self) -> bool:
        """Begin queueing new work; let in-flight work finish."""
        return False

    def unpause(self) -> bool:
        """Resume normal operation after :meth:`pause`."""
        return False

    def restart(self) -> bool:
        """Graceful shutdown followed by start."""
        return False

    @abstractmethod
    def shutdown(self) -> bool:
        """Teardown is imminent and may not be clean."""

    def graceful_shutdown(self) -> bool:
        """Ideal clean teardown."""
        return self.shutdown()


class Client(ABC):
    """A caller that a service can send a reply :class:`Envelope` back to.

    Ports ``ra.common.Client``.
    """

    @abstractmethod
    def reply(self, envelope: "Envelope") -> None:
        """Deliver a reply to the client."""
