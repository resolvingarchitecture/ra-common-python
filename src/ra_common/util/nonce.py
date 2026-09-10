"""Replay protection via a bounded set of seen ids. Ports ``ra.common.Nonce``.

The Java pruning bug (``max * (pct / 100)`` integer-divides to zero) is fixed
here: we compute ``max * pct // 100``.
"""

from __future__ import annotations

from collections import deque


class Nonce:
    """Tracks recently-seen ids and rejects duplicates."""

    def __init__(self, max_size: int = 1_000_000, prune_percent: int = 10) -> None:
        self._seen: set[int] = set()
        self._order: deque[int] = deque()
        self._max_size = max_size
        self._prune_percent = min(100, max(0, prune_percent))

    def continue_on(self, id_: int) -> bool:
        """Register ``id_``. Return ``True`` if new, ``False`` if a replay."""
        self._prune()
        if id_ in self._seen:
            return False
        self._seen.add(id_)
        self._order.append(id_)
        return True

    def __len__(self) -> int:
        return len(self._order)

    def is_empty(self) -> bool:
        return not self._order

    def _prune(self) -> None:
        if len(self._order) <= self._max_size:
            return
        if self._prune_percent == 100:
            self._seen.clear()
            self._order.clear()
            return
        to_prune = self._max_size * self._prune_percent // 100
        for _ in range(to_prune):
            if not self._order:
                break
            self._seen.discard(self._order.popleft())
