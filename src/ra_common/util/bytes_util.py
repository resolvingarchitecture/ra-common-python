"""Big/little-endian packing of a 4-byte slice to/from a signed 32-bit int.

Ports ``ra.common.BytesUtil``.
"""

from __future__ import annotations

_MASK = 0xFFFFFFFF


def _to_signed_32(value: int) -> int:
    value &= _MASK
    return value - 0x1_0000_0000 if value & 0x8000_0000 else value


def pack_big_endian(b: bytes) -> int:
    """Interpret the first four bytes of ``b`` as a big-endian signed int."""
    return _to_signed_32(int.from_bytes(b[:4], "big"))


def unpack_big_endian(x: int) -> bytes:
    """Encode ``x`` as four big-endian bytes."""
    return (x & _MASK).to_bytes(4, "big")


def pack_little_endian(b: bytes) -> int:
    """Interpret the first four bytes of ``b`` as a little-endian signed int."""
    return _to_signed_32(int.from_bytes(b[:4], "little"))


def unpack_little_endian(x: int) -> bytes:
    """Encode ``x`` as four little-endian bytes."""
    return (x & _MASK).to_bytes(4, "little")
