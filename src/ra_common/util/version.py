"""Loose version-string comparison. Ports ``ra.common.VersionComparator``.

Segments are separated by ``.``, ``_`` or ``-``. Within a segment every
non-digit character is ignored (``"8-ea"`` parses as ``8``). Segments are
compared numerically, left to right; the first difference decides. A string
that runs out of segments first sorts lower, so ``"2.0" < "2.0.0"``.
"""

from __future__ import annotations

_SEPARATORS = frozenset(".-_")


def _next_separator(s: str, start: int) -> int:
    i = start
    while i < len(s):
        if s[i] in _SEPARATORS:
            return i
        i += 1
    return i


def _parse_long(s: str, start: int, end: int) -> int:
    rv = 0
    parsed_any = False
    i = start
    while i < end and rv >= 0:
        c = s[i]
        if c.isdigit():
            parsed_any = True
            rv = rv * 10 + (ord(c) - ord("0"))
        i += 1
    return rv if parsed_any else -1


def version_compare(left: str, right: str) -> int:
    """Return ``-1``/``0``/``1`` comparing two version strings loosely."""
    if left == right:
        return 0
    ll, rl = len(left), len(right)
    il = ir = 0

    while True:
        if il >= ll:
            return 0 if ir >= rl else -1
        if ir >= rl:
            return 1

        lv = -1
        while lv == -1 and il < ll:
            nl = _next_separator(left, il)
            lv = _parse_long(left, il, nl)
            il = nl + 1

        rv = -1
        while rv == -1 and ir < rl:
            nr = _next_separator(right, ir)
            rv = _parse_long(right, ir, nr)
            ir = nr + 1

        if lv < rv:
            return -1
        if lv > rv:
            return 1
