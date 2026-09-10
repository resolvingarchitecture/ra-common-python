"""Ports ``ra.common.crypto.Addressable``."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Addressable(Protocol):
    """Something reachable on a network by its public key.

    It exposes a ``fingerprint`` and an ``address`` (the encoded public key).
    """

    fingerprint: str | None
    address: str | None
