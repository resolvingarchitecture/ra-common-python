"""The service framework: the ``Service`` / ``LifeCycle`` contract, shared
state, status enums and reports.

Ports the ``ra.common.service`` package (except ``ServiceDaemon``, deferred).
"""

from __future__ import annotations

from .base import RA_SERVICE_IMPL, Service, ServiceCore
from .message import NO_ERROR, REQUEST_REQUIRED, ServiceMessage
from .observer import ServiceStatusObserver
from .report import ServiceReport
from .status import ServiceLevel, ServiceStatus

__all__ = [
    "RA_SERVICE_IMPL",
    "Service",
    "ServiceCore",
    "NO_ERROR",
    "REQUEST_REQUIRED",
    "ServiceMessage",
    "ServiceStatusObserver",
    "ServiceReport",
    "ServiceLevel",
    "ServiceStatus",
]
