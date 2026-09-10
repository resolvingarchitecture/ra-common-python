"""Ports ``ra.common.service.ServiceReport``."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .._serde import compact
from .status import ServiceStatus


@dataclass
class ServiceReport:
    """A snapshot of a service's health, emitted with ``SERVICE_STATUS`` events
    and returned by ``Service.report``."""

    service_class_name: str
    service_status: ServiceStatus
    registered: bool = False
    running: bool = False
    version: str | None = None
    services_dependent_upon: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "service_class_name": self.service_class_name,
            "service_status": self.service_status.value,
            "registered": self.registered,
            "running": self.running,
            **compact({"version": self.version}),
        }
        if self.services_dependent_upon:
            out["services_dependent_upon"] = list(self.services_dependent_upon)
        return out

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ServiceReport":
        return cls(
            service_class_name=data["service_class_name"],
            service_status=ServiceStatus(data["service_status"]),
            registered=data.get("registered", False),
            running=data.get("running", False),
            version=data.get("version"),
            services_dependent_upon=list(data.get("services_dependent_upon", [])),
        )
