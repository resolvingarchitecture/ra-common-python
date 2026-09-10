"""Non-cryptographic random helpers. Ports ``ra.common.RandomUtil``.

Like the Java original these use a non-cryptographic PRNG. For salts and key
material use :mod:`ra_common.crypto` instead.
"""

from __future__ import annotations

import random
import string

_I64_MIN = -(2**63)
_I64_MAX = 2**63 - 1
_I32_MIN = -(2**31)
_I32_MAX = 2**31 - 1

_ALPHANUMERIC = string.ascii_letters + string.digits


def next_long() -> int:
    """A random 64-bit signed int across the full range (upper bound exclusive)."""
    return random.randrange(_I64_MIN, _I64_MAX)


def next_long_to(upper: int) -> int:
    return random.randrange(_I64_MIN, upper)


def next_long_in(lower: int, upper: int) -> int:
    return random.randrange(lower, upper)


def next_int() -> int:
    """A random 32-bit signed int across the full range (upper bound exclusive)."""
    return random.randrange(_I32_MIN, _I32_MAX)


def next_int_to(upper: int) -> int:
    return random.randrange(_I32_MIN, upper)


def next_int_in(lower: int, upper: int) -> int:
    return random.randrange(lower, upper)


def random_alphanumeric(length: int) -> str:
    """A random string of ``length`` characters drawn from ``[0-9A-Za-z]``."""
    return "".join(random.choices(_ALPHANUMERIC, k=length))


def random_bytes(count: int) -> bytes:
    return random.randbytes(count)
