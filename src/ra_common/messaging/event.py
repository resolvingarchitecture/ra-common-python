"""Ports ``ra.common.messaging.EventMessage``."""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Any

from .message import Message


class EventType(str, Enum):
    """Well-known event categories. Ports ``EventMessage.Type``.

    The wire form is a free-form string (``event_type``) so callers may use
    their own categories too; ``value`` is the ``SCREAMING_SNAKE`` name.
    """

    ERROR = "ERROR"
    EXCEPTION = "EXCEPTION"
    BUS_STATUS = "BUS_STATUS"
    PEER_STATUS = "PEER_STATUS"
    SERVICE_STATUS = "SERVICE_STATUS"
    DID_STATUS = "DID_STATUS"
    NETWORK_STATE_UPDATE = "NETWORK_STATE_UPDATE"
    PRICE_CHANGE = "PRICE_CHANGE"


class EventMessage(Message):
    """An event notification with an optional structured payload."""

    KIND = "event"

    def __init__(
        self,
        event_type: str,
        id: str | None = None,
        name: str | None = None,
        message: Any | None = None,
        error_messages: list[str] | None = None,
    ) -> None:
        self.error_messages = error_messages or []
        self.id = id or str(uuid.uuid4())
        self.event_type = event_type
        self.name = name
        self.message = message

    @classmethod
    def of(cls, event_type: EventType) -> "EventMessage":
        return cls(event_type.value)

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "kind": self.KIND,
            "id": self.id,
            "event_type": self.event_type,
        }
        if self.name is not None:
            out["name"] = self.name
        if self.message is not None:
            out["message"] = self.message
        if self.error_messages:
            out["error_messages"] = list(self.error_messages)
        return out

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EventMessage":
        return cls(
            event_type=data["event_type"],
            id=data.get("id"),
            name=data.get("name"),
            message=data.get("message"),
            error_messages=list(data.get("error_messages", [])),
        )
