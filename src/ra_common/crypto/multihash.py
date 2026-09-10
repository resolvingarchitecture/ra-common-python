"""A simplified multihash: a one-byte type code, a one-byte length, then the
digest. Ports ``ra.common.crypto.Multihash``.

Note this is the Java library's fixed-2-byte-header variant, **not** the full
varint multihash spec.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..encoding import base58_decode, base58_encode
from ..errors import InvalidInput

_CODES = {
    "Sha1": (0x11, 20),
    "Sha2_256": (0x12, 32),
    "Sha2_512": (0x13, 64),
    "Sha3": (0x14, 64),
    "Blake2b": (0x40, 64),
    "Blake2s": (0x41, 32),
}


class MultihashType(str, Enum):
    SHA1 = "Sha1"
    SHA2_256 = "Sha2_256"
    SHA2_512 = "Sha2_512"
    SHA3 = "Sha3"
    BLAKE2B = "Blake2b"
    BLAKE2S = "Blake2s"

    @property
    def code(self) -> int:
        return _CODES[self.value][0]

    @property
    def length(self) -> int:
        return _CODES[self.value][1]

    @classmethod
    def from_code(cls, code: int) -> "MultihashType":
        for name, (c, _) in _CODES.items():
            if c == code:
                return cls(name)
        raise InvalidInput(f"unknown multihash type: {code:#x}")


@dataclass(frozen=True)
class Multihash:
    """A digest tagged with its type."""

    kind: MultihashType
    digest: bytes

    def __post_init__(self) -> None:
        if len(self.digest) > 127:
            raise InvalidInput(f"unsupported hash size: {len(self.digest)}")
        if len(self.digest) != self.kind.length:
            raise InvalidInput(
                f"incorrect hash length: {len(self.digest)} != {self.kind.length}"
            )

    def to_bytes(self) -> bytes:
        return bytes([self.kind.code, len(self.digest)]) + self.digest

    @classmethod
    def from_bytes(cls, data: bytes) -> "Multihash":
        if len(data) < 2:
            raise InvalidInput("multihash too short")
        kind = MultihashType.from_code(data[0])
        length = data[1]
        if len(data) < 2 + length:
            raise InvalidInput("multihash truncated")
        return cls(kind, bytes(data[2:2 + length]))

    def to_hex(self) -> str:
        return self.to_bytes().hex()

    @classmethod
    def from_hex(cls, text: str) -> "Multihash":
        return cls.from_bytes(bytes.fromhex(text))

    def to_base58(self) -> str:
        return base58_encode(self.to_bytes())

    @classmethod
    def from_base58(cls, text: str) -> "Multihash":
        return cls.from_bytes(base58_decode(text))

    def __str__(self) -> str:
        return self.to_base58()

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.kind.value, "hash": list(self.digest)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Multihash":
        return cls(MultihashType(data["type"]), bytes(data["hash"]))
