"""Ports ``ra.common.identity.PIIClearable``."""

from __future__ import annotations

from abc import ABC, abstractmethod


class PiiClearable(ABC):
    """Implemented by types carrying personally-identifiable information.

    Provides a way to scrub it (typically before handing a copy to another party).
    """

    @abstractmethod
    def clear_sensitive(self) -> None:
        """Null out / reset every field that carries PII."""
