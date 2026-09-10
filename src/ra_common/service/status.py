"""Ports ``ra.common.service.{ServiceStatus, ServiceLevel}``."""

from __future__ import annotations

from enum import Enum


class ServiceLevel(str, Enum):
    """Delivery guarantee for an envelope. Ports ``ServiceLevel``."""

    AT_MOST_ONCE = "AtMostOnce"
    AT_LEAST_ONCE = "AtLeastOnce"
    EXACTLY_ONCE = "ExactlyOnce"


class ServiceStatus(str, Enum):
    """Detailed lifecycle state of a service."""

    NOT_INITIALIZED = "NotInitialized"
    INITIALIZING = "Initializing"
    WAITING = "Waiting"
    STARTING = "Starting"
    RUNNING = "Running"
    VERIFIED = "Verified"
    PARTIALLY_RUNNING = "PartiallyRunning"
    DEGRADED_RUNNING = "DegradedRunning"
    UNSTABLE = "Unstable"
    PAUSING = "Pausing"
    PAUSED = "Paused"
    UNPAUSING = "Unpausing"
    SHUTTING_DOWN = "ShuttingDown"
    GRACEFULLY_SHUTTING_DOWN = "GracefullyShuttingDown"
    SHUTDOWN = "Shutdown"
    GRACEFULLY_SHUTDOWN = "GracefullyShutdown"
    RESTARTING = "Restarting"
    UNAVAILABLE = "Unavailable"
    ERROR = "Error"

    def is_running(self) -> bool:
        return self in (
            ServiceStatus.RUNNING,
            ServiceStatus.VERIFIED,
            ServiceStatus.PARTIALLY_RUNNING,
            ServiceStatus.DEGRADED_RUNNING,
        )
