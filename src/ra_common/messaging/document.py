"""Ports ``ra.common.messaging.DocumentMessage``."""

from __future__ import annotations

from typing import Any

from .message import Message

#: Keys used by :class:`ra_common.envelope.Envelope` within ``data[0]``.
CONTENT = "CONTENT"
#: Key for a domain entity payload.
ENTITY = "ENTITY"
#: Key for the list of accumulated exceptions.
EXCEPTIONS = "EXCEPTIONS"


class DocumentMessage(Message):
    """A message carrying one or more named-value payload buckets.

    ``data[0]`` is the primary bucket used by the ``Envelope``
    content/entity/NVP helpers.
    """

    KIND = "document"

    def __init__(
        self,
        data: list[dict[str, Any]] | None = None,
        error_messages: list[str] | None = None,
    ) -> None:
        self.error_messages = error_messages or []
        self.data = data if data is not None else [{}]

    def primary(self) -> dict[str, Any]:
        if not self.data:
            self.data.append({})
        return self.data[0]

    def get(self, key: str) -> Any | None:
        return self.data[0].get(key) if self.data else None

    def put(self, key: str, value: Any) -> None:
        self.primary()[key] = value

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"kind": self.KIND, "data": self.data}
        if self.error_messages:
            out["error_messages"] = list(self.error_messages)
        return out

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DocumentMessage":
        return cls(
            data=list(data.get("data", [{}])),
            error_messages=list(data.get("error_messages", [])),
        )
