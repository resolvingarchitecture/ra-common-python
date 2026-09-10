"""The :class:`Route` hierarchy and its shared metadata.

Ports ``ra.common.route.{Route, BaseRoute, SimpleRoute}``. The Java abstract
base + reflective ``Class.forName`` polymorphism becomes a small class
hierarchy with a ``type`` tag on the wire (``simple``, ``routing_slip``,
``simple_external``, ``relayed_external``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .._serde import compact
from ..util.random_util import next_long


@dataclass
class RouteMeta:
    """Fields every route carries (``ra.common.route.BaseRoute``)."""

    service: str | None = None
    operation: str | None = None
    routed: bool = False
    route_id: int = field(default_factory=next_long)

    @classmethod
    def of(cls, service: str, operation: str) -> "RouteMeta":
        return cls(service=service, operation=operation)

    def to_dict(self) -> dict[str, Any]:
        return {
            **compact({"service": self.service, "operation": self.operation}),
            "routed": self.routed,
            "route_id": self.route_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RouteMeta":
        return cls(
            service=data.get("service"),
            operation=data.get("operation"),
            routed=data.get("routed", False),
            route_id=data.get("route_id", 0),
        )


class Route:
    """Base class for every route variant. Concrete subclasses set ``TYPE``."""

    TYPE: str = "route"
    meta: RouteMeta

    @property
    def service(self) -> str | None:
        return self.meta.service

    @property
    def operation(self) -> str | None:
        return self.meta.operation

    @property
    def routed(self) -> bool:
        return self.meta.routed

    @routed.setter
    def routed(self, value: bool) -> None:
        self.meta.routed = value

    @property
    def route_id(self) -> int:
        return self.meta.route_id

    @route_id.setter
    def route_id(self, value: int) -> None:
        self.meta.route_id = value

    def to_dict(self) -> dict[str, Any]:  # pragma: no cover - overridden
        raise NotImplementedError


@dataclass
class SimpleRoute(Route):
    """A single in-process route: a ``service`` and an ``operation`` on it."""

    TYPE = "simple"
    meta: RouteMeta = field(default_factory=RouteMeta)

    @classmethod
    def new(cls, service: str, operation: str) -> "SimpleRoute":
        return cls(meta=RouteMeta.of(service, operation))

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.TYPE, "meta": self.meta.to_dict()}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SimpleRoute":
        return cls(meta=RouteMeta.from_dict(data.get("meta", {})))


def route_from_dict(data: dict[str, Any]) -> Route:
    """Rebuild a route from its tagged dict."""
    from .external import RelayedExternalRoute, SimpleExternalRoute
    from .slip import DynamicRoutingSlip

    tag = data.get("type")
    if tag == "simple":
        return SimpleRoute.from_dict(data)
    if tag == "routing_slip":
        return DynamicRoutingSlip.from_dict(data)
    if tag == "simple_external":
        return SimpleExternalRoute.from_dict(data)
    if tag == "relayed_external":
        return RelayedExternalRoute.from_dict(data)
    raise ValueError(f"unknown route type: {tag!r}")
