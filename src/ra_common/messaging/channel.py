"""Producer / consumer / channel / bus contracts.

Ports ``ra.common.messaging.{MessageProducer, MessageConsumer, MessageChannel,
MessageBus}``. Concrete broker implementations (seda-bus etc.) live outside this
package.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ..lifecycle import Client, LifeCycle

if TYPE_CHECKING:
    from ..envelope import Envelope
    from ..service.status import ServiceLevel


class MessageProducer(ABC):
    """Sends envelopes onward. Ports ``MessageProducer``."""

    @abstractmethod
    def send(self, envelope: "Envelope") -> bool:
        """Send ``envelope``. Return ``True`` if accepted."""

    def send_with_callback(self, envelope: "Envelope", callback: Client) -> bool:
        """Send ``envelope``, delivering the reply to ``callback``."""
        return self.send(envelope)

    def dead_letter(self, envelope: "Envelope") -> bool:
        """Route ``envelope`` to the dead-letter sink."""
        return False


class MessageConsumer(ABC):
    """Receives envelopes. Ports ``MessageConsumer``."""

    @abstractmethod
    def receive(self, envelope: "Envelope") -> bool:
        """Handle ``envelope``. Return ``True`` if handled."""


class MessageChannel(MessageProducer, LifeCycle):
    """A named, bounded queue between stages. Ports ``MessageChannel``."""

    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def is_pub_sub(self) -> bool: ...

    @abstractmethod
    def queued(self) -> int: ...

    @abstractmethod
    def ack(self, envelope: "Envelope") -> None: ...


class MessageBus(LifeCycle):
    """Registers channels and publishes envelopes across them. Ports ``MessageBus``."""

    @abstractmethod
    def register_channel(
        self, name: str, service_level: "ServiceLevel | None" = None
    ) -> bool: ...

    @abstractmethod
    def publish(self, envelope: "Envelope") -> bool: ...

    def publish_with_callback(self, envelope: "Envelope", callback: Client) -> bool:
        return self.publish(envelope)

    @abstractmethod
    def completed(self, envelope: "Envelope") -> bool: ...
