"""Ports ``ra.common.service.ServiceStatusObserver``."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .status import ServiceStatus


class ServiceStatusObserver(ABC):
    """Notified whenever a service's status changes."""

    @abstractmethod
    def service_status_changed(
        self, service_full_name: str, status: ServiceStatus
    ) -> None: ...
