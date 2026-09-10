"""Ports ``ra.common.identity.PublicKey``."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .._serde import compact
from .signature import Signature


@dataclass
class PublicKey:
    """A public key plus how it is encoded and any (optionally signed) attributes.

    The key material itself lives in :attr:`address` (the encoded key string);
    the ``is_*`` flags say which encoding was used.
    """

    alias: str | None = None
    fingerprint: str | None = None
    address: str | None = None
    key_type: str | None = None
    is_identity_key: bool = False
    is_encryption_key: bool = False
    is_base64_encoded: bool = False
    is_base58_encoded: bool = False
    is_pem: bool = False
    is_hex: bool = False
    attributes: dict[str, Any] = field(default_factory=dict)
    signed_attributes: dict[str, list[Signature]] = field(default_factory=dict)

    @classmethod
    def from_address(cls, address: str) -> "PublicKey":
        return cls(address=address)

    def add_attribute(self, name: str, value: Any) -> None:
        self.attributes[name] = value

    def attribute(self, name: str) -> Any:
        return self.attributes.get(name)

    def add_signed_attribute(self, name: str, signature: Signature) -> None:
        self.signed_attributes.setdefault(name, []).append(signature)

    def remove_signature(self, name: str, signed_by_address: str) -> None:
        sigs = self.signed_attributes.get(name)
        if sigs is not None:
            self.signed_attributes[name] = [
                s for s in sigs if s.signed_by_address != signed_by_address
            ]

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = compact(
            {
                "alias": self.alias,
                "fingerprint": self.fingerprint,
                "address": self.address,
                "type": self.key_type,
            }
        )
        for flag in (
            "is_identity_key",
            "is_encryption_key",
            "is_base64_encoded",
            "is_base58_encoded",
            "is_pem",
            "is_hex",
        ):
            if getattr(self, flag):
                out[flag] = True
        if self.attributes:
            out["attributes"] = dict(self.attributes)
        if self.signed_attributes:
            out["signed_attributes"] = {
                k: [s.to_dict() for s in v] for k, v in self.signed_attributes.items()
            }
        return out

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PublicKey":
        return cls(
            alias=data.get("alias"),
            fingerprint=data.get("fingerprint"),
            address=data.get("address"),
            key_type=data.get("type"),
            is_identity_key=data.get("is_identity_key", False),
            is_encryption_key=data.get("is_encryption_key", False),
            is_base64_encoded=data.get("is_base64_encoded", False),
            is_base58_encoded=data.get("is_base58_encoded", False),
            is_pem=data.get("is_pem", False),
            is_hex=data.get("is_hex", False),
            attributes=dict(data.get("attributes", {})),
            signed_attributes={
                k: [Signature.from_dict(s) for s in v]
                for k, v in data.get("signed_attributes", {}).items()
            },
        )
