"""The universal message wrapper passed between services.

Ports ``ra.common.Envelope`` (and folds in the useful parts of the deprecated
``ra.common.DLC`` static helpers as methods).
"""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Any

from ._serde import compact
from .file import Multipart
from .identity import Did
from .messaging import (
    CONTENT,
    ENTITY,
    EXCEPTIONS,
    CommandMessage,
    DocumentMessage,
    EventMessage,
    EventType,
    Message,
    TextMessage,
    message_from_dict,
)
from .route import DynamicRoutingSlip, Route, SimpleExternalRoute, SimpleRoute, route_from_dict
from .service.status import ServiceLevel

HEADER_AUTHORIZATION = "Authorization"
HEADER_CONTENT_DISPOSITION = "Content-Disposition"
HEADER_CONTENT_TRANSFER_ENCODING = "Content-Transfer-Encoding"
HEADER_CONTENT_TYPE = "Content-Type"
HEADER_CONTENT_TYPE_JSON = "application/json"
HEADER_USER_AGENT = "User-Agent"


class MessageType(str, Enum):
    DOCUMENT = "Document"
    TEXT = "Text"
    EVENT = "Event"
    COMMAND = "Command"
    NONE = "None"


class Action(str, Enum):
    POST = "Post"
    PUT = "Put"
    DELETE = "Delete"
    GET = "Get"


class Envelope:
    """Wraps everything passed around the application so there is always a place
    for header/routing metadata."""

    def __init__(self, id: str | None = None, message: Message | None = None) -> None:
        self.id = id or str(uuid.uuid4())
        self.dynamic_routing_slip = DynamicRoutingSlip()
        self.route: Route | None = None
        self.markers: list[str] = []
        self.did = Did()
        self.client: str | None = None
        self.reply_to_client = False
        self.client_reply_action: str | None = None
        self.url: str | None = None
        self.multipart: Multipart | None = None
        self.action: Action | None = None
        self.command_path: str | None = None
        self.headers: dict[str, Any] = {}
        self.message = message
        self.sensitivity = 1
        self.delayed = False
        self.min_delay = 0
        self.max_delay = 0
        self.copy = False
        self.max_copies = 0
        self.min_copies = 0
        self.service_level = ServiceLevel.AT_LEAST_ONCE

    # ---- factories -----------------------------------------------------

    @classmethod
    def command(cls) -> "Envelope":
        return cls(message=CommandMessage())

    @classmethod
    def document(cls) -> "Envelope":
        return cls(message=DocumentMessage())

    @classmethod
    def document_with_id(cls, id: str) -> "Envelope":
        return cls(id=id, message=DocumentMessage())

    @classmethod
    def headers_only(cls) -> "Envelope":
        return cls()

    @classmethod
    def event(cls, event_type: EventType) -> "Envelope":
        return cls(message=EventMessage.of(event_type))

    @classmethod
    def text(cls) -> "Envelope":
        return cls(message=TextMessage())

    # ---- headers -----------------------------------------------------

    def set_header(self, name: str, value: Any) -> None:
        self.headers[name] = value

    def header_exists(self, name: str) -> bool:
        return name in self.headers

    def remove_header(self, name: str) -> None:
        self.headers.pop(name, None)

    def header(self, name: str) -> Any | None:
        return self.headers.get(name)

    def content_type(self) -> str | None:
        value = self.headers.get(HEADER_CONTENT_TYPE)
        return value if isinstance(value, str) else None

    def set_content_type(self, content_type: str) -> None:
        self.headers[HEADER_CONTENT_TYPE] = content_type

    # ---- routing ---------------------------------------------------

    def get_route(self) -> Route | None:
        """The route currently being processed; falls back to the slip's current route."""
        if self.route is None:
            current = self.dynamic_routing_slip.current_route()
            if current is not None:
                self.route = current
        return self.route

    def ratchet(self) -> None:
        """Advance to the next route in the slip."""
        self.route = self.dynamic_routing_slip.next_route()

    def add_route(self, service: str, operation: str) -> None:
        self.dynamic_routing_slip.add_route(SimpleRoute.new(service, operation))

    def add_external_route(self, service: str, operation: str) -> None:
        self.dynamic_routing_slip.add_route(SimpleExternalRoute.new(service, operation))

    # ---- document payload accessors ------------------------------

    def _doc(self) -> DocumentMessage | None:
        return self.message if isinstance(self.message, DocumentMessage) else None

    def add_content(self, content: Any) -> bool:
        doc = self._doc()
        if doc is None:
            return False
        doc.put(CONTENT, content)
        return True

    def content(self) -> Any | None:
        doc = self._doc()
        return doc.get(CONTENT) if doc else None

    def add_entity(self, entity: Any) -> bool:
        doc = self._doc()
        if doc is None:
            return False
        doc.put(ENTITY, entity)
        return True

    def entity(self) -> Any | None:
        doc = self._doc()
        return doc.get(ENTITY) if doc else None

    def add_exception(self, message: str) -> bool:
        doc = self._doc()
        if doc is None:
            return False
        bucket = doc.primary()
        existing = bucket.get(EXCEPTIONS)
        if isinstance(existing, list):
            existing.append(message)
        else:
            bucket[EXCEPTIONS] = [message]
        return True

    def exceptions(self) -> list[str]:
        doc = self._doc()
        value = doc.get(EXCEPTIONS) if doc else None
        return list(value) if isinstance(value, list) else []

    def add_error_message(self, message: str) -> None:
        if self.message is not None:
            self.message.add_error_message(message)

    def error_messages(self) -> list[str]:
        return list(self.message.error_messages) if self.message is not None else []

    def add_nvp(self, name: str, value: Any) -> bool:
        doc = self._doc()
        if doc is None:
            return False
        doc.put(name, value)
        return True

    def value(self, name: str) -> Any | None:
        doc = self._doc()
        return doc.get(name) if doc else None

    def values(self) -> dict[str, Any] | None:
        doc = self._doc()
        return doc.data[0] if doc and doc.data else None

    # ---- markers -------------------------------------------------

    def marker_present(self, marker: str) -> bool:
        return marker in self.markers

    def mark(self, marker: str) -> None:
        self.markers.append(marker)

    # ---- serialization ------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "id": self.id,
            "dynamic_routing_slip": self.dynamic_routing_slip.to_dict(),
            "markers": list(self.markers),
            "did": self.did.to_dict(),
            "reply_to_client": self.reply_to_client,
            "headers": self.headers,
            "sensitivity": self.sensitivity,
            "delayed": self.delayed,
            "min_delay": self.min_delay,
            "max_delay": self.max_delay,
            "copy": self.copy,
            "max_copies": self.max_copies,
            "min_copies": self.min_copies,
            "service_level": self.service_level.value,
            **compact(
                {
                    "route": self.route.to_dict() if self.route else None,
                    "client": self.client,
                    "client_reply_action": self.client_reply_action,
                    "url": self.url,
                    "multipart": self.multipart.to_dict() if self.multipart else None,
                    "action": self.action.value if self.action else None,
                    "command_path": self.command_path,
                    "message": self.message.to_dict() if self.message else None,
                }
            ),
        }
        return out

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Envelope":
        env = cls(id=data.get("id"))
        if data.get("dynamic_routing_slip"):
            env.dynamic_routing_slip = DynamicRoutingSlip.from_dict(data["dynamic_routing_slip"])
        env.route = route_from_dict(data["route"]) if data.get("route") else None
        env.markers = list(data.get("markers", []))
        if data.get("did"):
            env.did = Did.from_dict(data["did"])
        env.client = data.get("client")
        env.reply_to_client = data.get("reply_to_client", False)
        env.client_reply_action = data.get("client_reply_action")
        env.url = data.get("url")
        env.multipart = Multipart.from_dict(data["multipart"]) if data.get("multipart") else None
        env.action = Action(data["action"]) if data.get("action") else None
        env.command_path = data.get("command_path")
        env.headers = dict(data.get("headers", {}))
        env.message = message_from_dict(data["message"]) if data.get("message") else None
        env.sensitivity = data.get("sensitivity", 1)
        env.delayed = data.get("delayed", False)
        env.min_delay = data.get("min_delay", 0)
        env.max_delay = data.get("max_delay", 0)
        env.copy = data.get("copy", False)
        env.max_copies = data.get("max_copies", 0)
        env.min_copies = data.get("min_copies", 0)
        env.service_level = ServiceLevel(
            data.get("service_level", ServiceLevel.AT_LEAST_ONCE.value)
        )
        return env

    def to_json(self, *, indent: int | None = 2) -> str:
        import json

        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, text: str) -> "Envelope":
        import json

        return cls.from_dict(json.loads(text))

    # ---- identity / equality -----------------------------------

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Envelope) and other.id == self.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"Envelope(id={self.id!r})"
