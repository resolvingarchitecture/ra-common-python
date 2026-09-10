"""Ports ``ra.common.messaging.Email``."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .._serde import compact

MIMETYPE_TEXT_PLAIN = "text/plain"


@dataclass
class Email:
    """A simple email record. Not a :class:`Message` - a persistable value type."""

    to: str | None = None
    from_: str | None = None
    subject: str | None = None
    message: str | None = None
    id: int | None = None
    message_type: str = MIMETYPE_TEXT_PLAIN
    flag: int = 0

    @classmethod
    def anonymous(cls, to: str, subject: str, message: str) -> "Email":
        return cls(to=to, subject=subject, message=message)

    def to_dict(self) -> dict[str, Any]:
        return {
            **compact(
                {
                    "id": self.id,
                    "to": self.to,
                    "from": self.from_,
                    "subject": self.subject,
                    "message": self.message,
                }
            ),
            "message_type": self.message_type,
            "flag": self.flag,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Email":
        return cls(
            to=data.get("to"),
            from_=data.get("from"),
            subject=data.get("subject"),
            message=data.get("message"),
            id=data.get("id"),
            message_type=data.get("message_type", MIMETYPE_TEXT_PLAIN),
            flag=data.get("flag", 0),
        )
