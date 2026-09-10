"""Ports ``ra.common.messaging.TextMessage``."""

from __future__ import annotations

from typing import Any

from ..identity import Did
from .message import Message


class TextMessage(Message):
    """A plain text message between two identities."""

    KIND = "text"

    def __init__(
        self,
        to: Did | None = None,
        from_: Did | None = None,
        text: str | None = None,
        error_messages: list[str] | None = None,
    ) -> None:
        self.error_messages = error_messages or []
        self.to = to
        self.from_ = from_
        self.text = text

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"kind": self.KIND}
        if self.to is not None:
            out["to"] = self.to.to_dict()
        if self.from_ is not None:
            out["from"] = self.from_.to_dict()
        if self.text is not None:
            out["text"] = self.text
        if self.error_messages:
            out["error_messages"] = list(self.error_messages)
        return out

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TextMessage":
        return cls(
            to=Did.from_dict(data["to"]) if data.get("to") else None,
            from_=Did.from_dict(data["from"]) if data.get("from") else None,
            text=data.get("text"),
            error_messages=list(data.get("error_messages", [])),
        )
