"""Ports ``ra.common.service.ServiceMessage``."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .._serde import compact

#: Sentinel status code meaning "no error".
NO_ERROR = -1
#: Sentinel status code meaning "a request is required".
REQUEST_REQUIRED = 0


@dataclass
class ServiceMessage:
    """Base shape for service request/response messages: a status code plus
    optional error text. Concrete services extend this with their own fields."""

    status_code: int = NO_ERROR
    error_message: str | None = None
    exception: str | None = None
    kind: str | None = None

    def is_error(self) -> bool:
        return self.status_code != NO_ERROR or self.error_message is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status_code": self.status_code,
            **compact(
                {
                    "error_message": self.error_message,
                    "exception": self.exception,
                    "type": self.kind,
                }
            ),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ServiceMessage":
        return cls(
            status_code=data.get("status_code", NO_ERROR),
            error_message=data.get("error_message"),
            exception=data.get("exception"),
            kind=data.get("type"),
        )
