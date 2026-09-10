"""Hashcash proof-of-work tokens (v0 and v1). Ports ``ra.common.HashCash``.

A token is ``version:[bits:]YYMMDD:resource:ext:rand:counter``; its "value" is
the number of leading zero **bits** in ``SHA1(token)``. Minting searches
``counter`` until that value reaches the requested difficulty.
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from ..errors import InvalidInput

_HASH_BITS = 160


def _leading_zero_bits(data: bytes) -> int:
    total = 0
    for byte in data:
        if byte == 0:
            total += 8
        else:
            total += 8 - byte.bit_length()
            break
    return total


def _sha1_bits(token: str) -> int:
    return _leading_zero_bits(hashlib.sha1(token.encode("utf-8")).digest())


def _serialize_extensions(ext: dict[str, list[str]]) -> str:
    if not ext:
        return ""
    parts: list[str] = []
    for key, values in ext.items():
        if any(c in key for c in ":;="):
            raise InvalidInput(f"illegal char in extension key: {key}")
        if values:
            for v in values:
                if any(c in v for c in ":;,"):
                    raise InvalidInput(f"illegal char in extension value: {v}")
            parts.append(f"{key}={','.join(values)}")
        else:
            parts.append(key)
    return ";".join(parts)


def _deserialize_extensions(text: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    if not text:
        return out
    for item in text.split(";"):
        key, sep, value = item.partition("=")
        out[key] = value.split(",") if sep else []
    return out


@dataclass
class HashCash:
    """A minted or parsed hashcash token."""

    token: str
    value: int
    resource: str
    date: date
    version: int
    extensions: dict[str, list[str]] = field(default_factory=dict)

    @classmethod
    def mint(cls, resource: str, bits: int) -> "HashCash":
        """Mint a v1 token for ``resource`` at ``bits`` difficulty, dated today (UTC)."""
        return cls.mint_with(resource, {}, datetime.now(timezone.utc).date(), bits, 1)

    @classmethod
    def mint_with(
        cls,
        resource: str,
        extensions: dict[str, list[str]],
        on: date,
        bits: int,
        version: int,
    ) -> "HashCash":
        if version > 1:
            raise InvalidInput("only hashcash versions 0 and 1 are supported")
        if bits > _HASH_BITS:
            raise InvalidInput("value must be between 0 and 160")
        if ":" in resource:
            raise InvalidInput("resource may not contain a colon")
        ext_str = _serialize_extensions(extensions)
        date_str = on.strftime("%y%m%d")
        if version == 0:
            prefix = f"0:{date_str}:{resource}:{ext_str}:"
        else:
            prefix = f"1:{bits}:{date_str}:{resource}:{ext_str}:"
        token = cls._generate(prefix, bits)
        value = _sha1_bits(token) if version == 0 else bits
        return cls(token, value, resource, on, version, dict(extensions))

    @staticmethod
    def _generate(prefix: str, bits: int) -> str:
        rnd = secrets.randbits(64)
        counter = secrets.randbits(64)
        stem = f"{prefix}{rnd:x}:"
        while True:
            counter += 1
            candidate = f"{stem}{counter:x}"
            if _sha1_bits(candidate) >= bits:
                return candidate

    @classmethod
    def parse(cls, token: str) -> "HashCash":
        parts = token.split(":")
        try:
            version = int(parts[0])
        except (ValueError, IndexError):
            raise InvalidInput("bad hashcash version") from None
        expected = {0: 6, 1: 7}.get(version)
        if expected is None:
            raise InvalidInput("only hashcash versions 0 and 1 are supported")
        if len(parts) != expected:
            raise InvalidInput("improperly formed hashcash")
        idx = 1
        claimed_bits = 0
        if version == 1:
            try:
                claimed_bits = int(parts[idx])
            except ValueError:
                raise InvalidInput("bad hashcash bits") from None
            idx += 1
        try:
            on = datetime.strptime(parts[idx], "%y%m%d").date()
        except ValueError as exc:
            raise InvalidInput(f"bad hashcash date: {exc}") from None
        idx += 1
        resource = parts[idx]
        idx += 1
        extensions = _deserialize_extensions(parts[idx])
        actual = _sha1_bits(token)
        value = actual if version == 0 else min(actual, claimed_bits)
        return cls(token, value, resource, on, version, extensions)

    def computed_bits(self) -> int:
        """The leading-zero-bit count actually present in ``SHA1(token)``."""
        return _sha1_bits(self.token)

    def is_valid_for(self, resource: str, min_bits: int) -> bool:
        return self.resource == resource and self.computed_bits() >= min_bits

    def __str__(self) -> str:
        return self.token
