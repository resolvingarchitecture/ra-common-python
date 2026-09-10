"""Ports ``ra.common.identity.DID`` (Decentralized IDentification)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .._serde import compact
from ..crypto.hash import Hash, HashAlgorithm
from .pii import PiiClearable
from .public_key import PublicKey


class DidStatus(str, Enum):
    INACTIVE = "Inactive"
    ACTIVE = "Active"
    SUSPENDED = "Suspended"
    PRIVATE = "Private"


class DidType(str, Enum):
    CONTACT = "Contact"
    IDENTITY = "Identity"
    NODE = "Node"


@dataclass
class Did(PiiClearable):
    """A decentralized identity: a username, an optional passphrase (+ its hash),
    and a :class:`PublicKey`.

    Deliberately does not follow the W3C DID spec - RA models each key as its
    own identity rather than grouping keys.
    """

    username: str = "Anon"
    passphrase: str | None = None
    passphrase2: str | None = None
    passphrase_hash: Hash | None = None
    passphrase_hash_algorithm: HashAlgorithm = HashAlgorithm.PBKDF2_HMAC_SHA1
    description: str = ""
    status: DidStatus = DidStatus.INACTIVE
    did_type: DidType = DidType.IDENTITY
    verified: bool = False
    authenticated: bool = False
    public_key: PublicKey = field(default_factory=PublicKey)

    @classmethod
    def with_username(cls, username: str) -> "Did":
        return cls(username=username)

    def effective_passphrase_hash_algorithm(self) -> HashAlgorithm:
        """The algorithm recorded on the stored hash, if any, else the default."""
        if self.passphrase_hash is not None:
            return self.passphrase_hash.algorithm
        return self.passphrase_hash_algorithm

    def clear_sensitive(self) -> None:
        self.username = ""
        self.passphrase = None
        self.passphrase2 = None
        self.description = ""
        self.status = DidStatus.PRIVATE
        self.verified = False
        self.authenticated = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "username": self.username,
            **compact(
                {
                    "passphrase": self.passphrase,
                    "passphrase2": self.passphrase2,
                    "passphrase_hash": (
                        self.passphrase_hash.to_dict() if self.passphrase_hash else None
                    ),
                }
            ),
            "passphrase_hash_algorithm": self.passphrase_hash_algorithm.value,
            "description": self.description,
            "status": self.status.value,
            "did_type": self.did_type.value,
            "verified": self.verified,
            "authenticated": self.authenticated,
            "public_key": self.public_key.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Did":
        raw_hash = data.get("passphrase_hash")
        return cls(
            username=data.get("username", "Anon"),
            passphrase=data.get("passphrase"),
            passphrase2=data.get("passphrase2"),
            passphrase_hash=Hash.from_dict(raw_hash) if raw_hash else None,
            passphrase_hash_algorithm=HashAlgorithm(
                data.get("passphrase_hash_algorithm", HashAlgorithm.PBKDF2_HMAC_SHA1.value)
            ),
            description=data.get("description", ""),
            status=DidStatus(data.get("status", DidStatus.INACTIVE.value)),
            did_type=DidType(data.get("did_type", DidType.IDENTITY.value)),
            verified=data.get("verified", False),
            authenticated=data.get("authenticated", False),
            public_key=PublicKey.from_dict(data.get("public_key", {})),
        )
