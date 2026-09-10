"""Ports ``ra.common.route.{ExternalRoute, SimpleExternalRoute, RelayedExternalRoute}``."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .._serde import compact
from ..network import NetworkPeer
from .model import Route, RouteMeta

#: Status codes an external route can carry (ports the ``ExternalRoute`` int constants).
external_status = {
    "DESTINATION_PEER_REQUIRED": 2,
    "DESTINATION_PEER_WRONG_NETWORK": 3,
    "DESTINATION_PEER_NOT_FOUND": 4,
    "NO_SERVICE": 7,
    "NO_OPERATION": 8,
    "NO_ADDRESS": 9,
    "NO_FINGERPRINT": 10,
    "NO_PORT": 11,
}


@dataclass
class SimpleExternalRoute(Route):
    """A route to a service on a remote peer."""

    TYPE = "simple_external"
    meta: RouteMeta = field(default_factory=RouteMeta)
    origination: NetworkPeer | None = None
    destination: NetworkPeer | None = None
    send_content_only: bool = False
    status_code: int = 0

    @classmethod
    def new(cls, service: str, operation: str) -> "SimpleExternalRoute":
        return cls(meta=RouteMeta.of(service, operation), send_content_only=True)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.TYPE,
            "meta": self.meta.to_dict(),
            **compact(
                {
                    "origination": self.origination.to_dict() if self.origination else None,
                    "destination": self.destination.to_dict() if self.destination else None,
                }
            ),
            "send_content_only": self.send_content_only,
            "status_code": self.status_code,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SimpleExternalRoute":
        return cls(
            meta=RouteMeta.from_dict(data.get("meta", {})),
            origination=(
                NetworkPeer.from_dict(data["origination"])
                if data.get("origination")
                else None
            ),
            destination=(
                NetworkPeer.from_dict(data["destination"])
                if data.get("destination")
                else None
            ),
            send_content_only=data.get("send_content_only", False),
            status_code=data.get("status_code", 0),
        )


@dataclass
class RelayedExternalRoute(Route):
    """An external route relayed through intermediate peers, with delay/copy/
    sensitivity controls."""

    TYPE = "relayed_external"
    base: SimpleExternalRoute = field(default_factory=SimpleExternalRoute)
    from_peer: NetworkPeer | None = None
    to_peer: NetworkPeer | None = None
    delayed: bool = False
    min_delay: int = 0
    max_delay: int = 0
    copy: bool = False
    min_copies: int = 0
    max_copies: int = 0
    sensitivity: int = 0

    @property
    def meta(self) -> RouteMeta:  # type: ignore[override]
        return self.base.meta

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.TYPE,
            "base": self.base.to_dict(),
            **compact(
                {
                    "from_peer": self.from_peer.to_dict() if self.from_peer else None,
                    "to_peer": self.to_peer.to_dict() if self.to_peer else None,
                }
            ),
            "delayed": self.delayed,
            "min_delay": self.min_delay,
            "max_delay": self.max_delay,
            "copy": self.copy,
            "min_copies": self.min_copies,
            "max_copies": self.max_copies,
            "sensitivity": self.sensitivity,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RelayedExternalRoute":
        return cls(
            base=SimpleExternalRoute.from_dict(data.get("base", {"type": "simple_external"})),
            from_peer=(
                NetworkPeer.from_dict(data["from_peer"]) if data.get("from_peer") else None
            ),
            to_peer=NetworkPeer.from_dict(data["to_peer"]) if data.get("to_peer") else None,
            delayed=data.get("delayed", False),
            min_delay=data.get("min_delay", 0),
            max_delay=data.get("max_delay", 0),
            copy=data.get("copy", False),
            min_copies=data.get("min_copies", 0),
            max_copies=data.get("max_copies", 0),
            sensitivity=data.get("sensitivity", 0),
        )
