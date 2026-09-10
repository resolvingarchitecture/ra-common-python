"""Base32 and Base58 string codecs.

Ports ``ra.common.Base32`` and ``ra.common.Base58``. Since this port is not
wire-compatible we use standard implementations:

- **base32**: RFC 4648, uppercase ``A-Z2-7``, no padding.
- **base58**: the Bitcoin alphabet.
"""

from __future__ import annotations

import base64

from .errors import DecodeError

_B58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_B58_INDEX = {c: i for i, c in enumerate(_B58_ALPHABET)}


def base32_encode(data: bytes) -> str:
    """Encode bytes as unpadded RFC 4648 base32 (``A-Z2-7``)."""
    return base64.b32encode(data).decode("ascii").rstrip("=")


def base32_decode(text: str) -> bytes:
    """Decode an unpadded RFC 4648 base32 string."""
    padded = text + "=" * (-len(text) % 8)
    try:
        return base64.b32decode(padded, casefold=False)
    except Exception as exc:  # noqa: BLE001
        raise DecodeError(str(exc)) from exc


def base58_encode(data: bytes) -> str:
    """Encode bytes as base58 (Bitcoin alphabet)."""
    n = int.from_bytes(data, "big")
    out = ""
    while n > 0:
        n, rem = divmod(n, 58)
        out = _B58_ALPHABET[rem] + out
    pad = 0
    for byte in data:
        if byte == 0:
            pad += 1
        else:
            break
    return _B58_ALPHABET[0] * pad + out


def base58_decode(text: str) -> bytes:
    """Decode a base58 (Bitcoin alphabet) string."""
    n = 0
    for ch in text:
        idx = _B58_INDEX.get(ch)
        if idx is None:
            raise DecodeError(f"invalid base58 character: {ch!r}")
        n = n * 58 + idx
    body = n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b""
    pad = 0
    for ch in text:
        if ch == _B58_ALPHABET[0]:
            pad += 1
        else:
            break
    return b"\x00" * pad + body
