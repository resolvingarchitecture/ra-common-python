"""A hash value paired with the algorithm that produced it.

Ports ``ra.common.crypto.Hash`` and its nested ``Algorithm`` enum.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..errors import InvalidInput


class HashAlgorithm(str, Enum):
    """Digest / key-derivation algorithm."""

    SHA1 = "Sha1"
    SHA256 = "Sha256"
    SHA512 = "Sha512"
    PBKDF2_HMAC_SHA1 = "Pbkdf2HmacSha1"

    @property
    def jca_name(self) -> str:
        """The JCA-style name (``"SHA-256"``, ``"PBKDF2WithHmacSHA1"``, ...)."""
        return {
            HashAlgorithm.SHA1: "SHA-1",
            HashAlgorithm.SHA256: "SHA-256",
            HashAlgorithm.SHA512: "SHA-512",
            HashAlgorithm.PBKDF2_HMAC_SHA1: "PBKDF2WithHmacSHA1",
        }[self]

    @classmethod
    def parse(cls, text: str) -> "HashAlgorithm":
        table = {
            "SHA-1": cls.SHA1, "SHA1": cls.SHA1, "Sha1": cls.SHA1,
            "SHA-256": cls.SHA256, "SHA256": cls.SHA256, "Sha256": cls.SHA256,
            "SHA-512": cls.SHA512, "SHA512": cls.SHA512, "Sha512": cls.SHA512,
            "PBKDF2WithHmacSHA1": cls.PBKDF2_HMAC_SHA1,
            "Pbkdf2HmacSha1": cls.PBKDF2_HMAC_SHA1,
        }
        try:
            return table[text]
        except KeyError:
            raise InvalidInput(f"unknown hash algorithm: {text}") from None


@dataclass
class Hash:
    """A hash string together with the algorithm used.

    Equality is on the hash string alone, matching the Java ``equals``/``hashCode``.
    """

    hash: str
    algorithm: HashAlgorithm = HashAlgorithm.SHA256

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Hash) and other.hash == self.hash

    def __hash__(self) -> int:
        return hash(self.hash)

    def __str__(self) -> str:
        return self.hash

    def to_dict(self) -> dict[str, Any]:
        return {"hash": self.hash, "algorithm": self.algorithm.value}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Hash":
        return cls(hash=data["hash"], algorithm=HashAlgorithm(data["algorithm"]))
