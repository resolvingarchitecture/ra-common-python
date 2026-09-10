"""Ports ``ra.common.identity.Signature``.

The Java ``toMap``/``fromMap`` were empty stubs - signature data was silently
dropped on serialization. This port implements them properly.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .._serde import compact


@dataclass
class Signature:
    """A detached signature over some value, describing who signed it and how.

    This package does not perform signing/verification; ``Signature`` is a
    metadata record carried inside :class:`ra_common.identity.PublicKey`.
    Equality is on ``signed_by_address``.
    """

    value_signed: str | None = None
    algorithm: str | None = None
    signed_date: datetime | None = None
    signed_by_username: str | None = None
    signed_by_fingerprint: str | None = None
    signed_by_address: str | None = None

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Signature)
            and self.signed_by_address is not None
            and self.signed_by_address == other.signed_by_address
        )

    def __hash__(self) -> int:
        return hash(self.signed_by_address)

    def to_dict(self) -> dict[str, Any]:
        return compact(
            {
                "value_signed": self.value_signed,
                "algorithm": self.algorithm,
                "signed_date": self.signed_date.isoformat() if self.signed_date else None,
                "signed_by_username": self.signed_by_username,
                "signed_by_fingerprint": self.signed_by_fingerprint,
                "signed_by_address": self.signed_by_address,
            }
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Signature":
        raw_date = data.get("signed_date")
        return cls(
            value_signed=data.get("value_signed"),
            algorithm=data.get("algorithm"),
            signed_date=datetime.fromisoformat(raw_date) if raw_date else None,
            signed_by_username=data.get("signed_by_username"),
            signed_by_fingerprint=data.get("signed_by_fingerprint"),
            signed_by_address=data.get("signed_by_address"),
        )
