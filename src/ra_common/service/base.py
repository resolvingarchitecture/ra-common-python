"""The ``Service`` contract and its shared state.

Ports ``ra.common.service.{Service, BaseService}``. ``BaseService``'s state
becomes :class:`ServiceCore` (which a concrete service holds) and its behaviour
becomes methods on the :class:`Service` base class.
"""

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from ..lifecycle import LifeCycle
from ..messaging.channel import MessageProducer
from .observer import ServiceStatusObserver
from .report import ServiceReport
from .status import ServiceStatus

if TYPE_CHECKING:
    from ..envelope import Envelope

#: The config key naming the service implementation class (used by ``ServiceDaemon``).
RA_SERVICE_IMPL = "ra.service.impl"


class ServiceCore:
    """State shared by every service (ports the ``BaseService`` fields)."""

    def __init__(self, service_class_name: str) -> None:
        self.service_class_name = service_class_name
        self.status = ServiceStatus.NOT_INITIALIZED
        self.registered = False
        self.version: str | None = None
        self.services_dependent_upon: list[str] = []
        self.config: dict[str, str] = {}
        self.producer: MessageProducer | None = None
        self.observer: ServiceStatusObserver | None = None

    def add_dependent_service(self, name: str) -> None:
        self.services_dependent_upon.append(name)

    def send(self, envelope: "Envelope") -> bool:
        return self.producer.send(envelope) if self.producer is not None else False

    def report(self) -> ServiceReport:
        return ServiceReport(
            service_class_name=self.service_class_name,
            service_status=self.status,
            registered=self.registered,
            running=self.status == ServiceStatus.RUNNING,
            version=self.version,
            services_dependent_upon=list(self.services_dependent_upon),
        )

    def update_status(self, status: ServiceStatus) -> None:
        """Change status; if it actually changed, notify the observer and publish
        a ``SERVICE_STATUS`` event routed to ``ra.notification.NotificationService``."""
        if self.status == status:
            return
        self.status = status
        if self.observer is not None:
            self.observer.service_status_changed(self.service_class_name, status)
        if self.producer is not None:
            from ..envelope import Envelope
            from ..messaging import EventMessage, EventType

            ev = EventMessage.of(EventType.SERVICE_STATUS)
            ev.message = self.report().to_dict()
            e = Envelope.event(EventType.SERVICE_STATUS)
            e.message = ev
            e.add_route("ra.notification.NotificationService", "PUBLISH")
            e.ratchet()
            self.send(e)


class Service(LifeCycle, ABC):
    """A message-driven service. Ports ``ra.common.service.Service`` + the
    reusable parts of ``BaseService``."""

    core: ServiceCore

    def handle_document(self, envelope: "Envelope") -> None:
        """Handle a document message. Default: ignore."""

    def handle_event(self, envelope: "Envelope") -> None:
        """Handle an event message. Default: ignore."""

    def handle_command(self, envelope: "Envelope") -> None:
        """Handle a command message. Default: dispatch to the matching lifecycle method."""
        from ..messaging import Command

        msg = envelope.message
        command = getattr(msg.as_command(), "command", None) if msg else None
        if command is None:
            return
        config = dict(self.core.config)
        if command is Command.START:
            self.start(config)
        elif command is Command.PAUSE:
            self.pause()
        elif command is Command.UNPAUSE:
            self.unpause()
        elif command is Command.RESTART:
            self.restart()
        elif command is Command.SHUTDOWN:
            self.shutdown()
        elif command is Command.GRACEFULLY_SHUTDOWN:
            self.graceful_shutdown()
        elif command is Command.REPORT:
            envelope.set_header("result", self.report().to_dict())

    def handle_headers(self, envelope: "Envelope") -> None:
        """Handle a headers-only envelope. Default: ignore."""

    def service_status(self) -> ServiceStatus:
        return self.core.status

    def report(self) -> ServiceReport:
        return self.core.report()

    def handle(self, envelope: "Envelope") -> "Envelope":
        """Dispatch ``envelope`` to the right handler by message kind and return it."""
        from ..messaging import CommandMessage, DocumentMessage, EventMessage

        msg = envelope.message
        if isinstance(msg, DocumentMessage):
            self.handle_document(envelope)
        elif isinstance(msg, EventMessage):
            self.handle_event(envelope)
        elif isinstance(msg, CommandMessage):
            self.handle_command(envelope)
        else:
            self.handle_headers(envelope)
        return envelope
