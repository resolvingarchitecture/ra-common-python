"""A fixed 32-byte identifier. Ports ``ra.common.UniqueId``."""

from __future__ import annotations

import base64
import secrets
from dataclasses import dataclass

from ..errors import DecodeError, InvalidInput

LENGTH = 32


@dataclass(frozen=True)
class UniqueId:
    """A 32-byte identifier, rendered as standard padded base64 (44 chars)."""

    value: bytes

    def __post_init__(self) -> None:
        if len(self.value) != LENGTH:
            raise InvalidInput(f"UniqueId must be {LENGTH} bytes, got {len(self.value)}")

    @classmethod
    def random(cls) -> "UniqueId":
        return cls(secrets.token_bytes(LENGTH))

    @classmethod
    def from_slice(cls, src: bytes, offset: int = 0) -> "UniqueId":
        end = offset + LENGTH
        if len(src) < end:
            raise InvalidInput("not enough bytes for UniqueId")
        return cls(bytes(src[offset:end]))

    @classmethod
    def from_base64(cls, text: str) -> "UniqueId":
        try:
            raw = base64.b64decode(text, validate=True)
        except (ValueError, Exception) as exc:  # noqa: BLE001
            raise DecodeError(str(exc)) from exc
        if len(raw) != LENGTH:
            raise DecodeError("UniqueId must be 32 bytes")
        return cls(raw)

    def as_bytes(self) -> bytes:
        return self.value

    def to_base64(self) -> str:
        return base64.b64encode(self.value).decode("ascii")

    def __str__(self) -> str:
        return self.to_base64()

    def __lt__(self, other: "UniqueId") -> bool:
        return self.value < other.value
