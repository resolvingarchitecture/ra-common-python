"""The :class:`Message` base class and its tagged-dict (de)serialization."""

from __future__ import annotations

from typing import Any


class Message:
    """Any message that can travel inside an :class:`ra_common.envelope.Envelope`.

    Concrete subclasses (``DocumentMessage``, ``CommandMessage``,
    ``EventMessage``, ``TextMessage``) set ``KIND`` and carry an
    ``error_messages`` list.
    """

    KIND: str = "message"
    error_messages: list[str]

    def add_error_message(self, msg: str) -> None:
        self.error_messages.append(msg)

    def clear_error_messages(self) -> None:
        self.error_messages.clear()

    def as_document(self) -> Any | None:
        from .document import DocumentMessage

        return self if isinstance(self, DocumentMessage) else None

    def as_command(self) -> Any | None:
        from .command import CommandMessage

        return self if isinstance(self, CommandMessage) else None

    def as_event(self) -> Any | None:
        from .event import EventMessage

        return self if isinstance(self, EventMessage) else None

    def as_text(self) -> Any | None:
        from .text import TextMessage

        return self if isinstance(self, TextMessage) else None

    def to_dict(self) -> dict[str, Any]:  # pragma: no cover - overridden
        raise NotImplementedError


def message_from_dict(data: dict[str, Any]) -> Message:
    from .command import CommandMessage
    from .document import DocumentMessage
    from .event import EventMessage
    from .text import TextMessage

    kind = data.get("kind")
    if kind == "document":
        return DocumentMessage.from_dict(data)
    if kind == "command":
        return CommandMessage.from_dict(data)
    if kind == "event":
        return EventMessage.from_dict(data)
    if kind == "text":
        return TextMessage.from_dict(data)
    raise ValueError(f"unknown message kind: {kind!r}")
