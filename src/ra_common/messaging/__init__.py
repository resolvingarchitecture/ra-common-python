"""Messages carried inside an :class:`ra_common.envelope.Envelope`.

Ports the ``ra.common.messaging`` package. The Java ``Message`` interface +
``BaseMessage`` + concrete subclasses become a small class hierarchy tagged with
``kind`` on the wire.
"""

from __future__ import annotations

from .channel import MessageBus, MessageChannel, MessageConsumer, MessageProducer
from .command import Command, CommandMessage
from .document import CONTENT, ENTITY, EXCEPTIONS, DocumentMessage
from .email import Email
from .event import EventMessage, EventType
from .message import Message, message_from_dict
from .text import TextMessage

__all__ = [
    "MessageBus",
    "MessageChannel",
    "MessageConsumer",
    "MessageProducer",
    "Command",
    "CommandMessage",
    "CONTENT",
    "ENTITY",
    "EXCEPTIONS",
    "DocumentMessage",
    "Email",
    "EventMessage",
    "EventType",
    "Message",
    "message_from_dict",
    "TextMessage",
]
