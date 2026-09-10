"""Ports ``ra.common.route.{RoutingSlip, DynamicRoutingSlip}``.

A LIFO stack of routes walked one hop at a time. The Java version serialized its
stack and rebuilt each entry reflectively (iterating backwards to restore stack
order); here it is a plain list round-trip with ``add_route`` pushing at the
front and ``next_route`` popping the front.
"""

from __future__ import annotations

from collections import deque
from typing import Any

from .model import Route, RouteMeta, route_from_dict


class DynamicRoutingSlip(Route):
    TYPE = "routing_slip"

    def __init__(
        self,
        meta: RouteMeta | None = None,
        routes: list[Route] | None = None,
        current_route: Route | None = None,
    ) -> None:
        self.meta = meta if meta is not None else RouteMeta()
        self._routes: deque[Route] = deque(routes or [])
        self._current_route = current_route

    def add_route(self, route: Route) -> None:
        """Push ``route`` onto the stack, stamping it with this slip's ``route_id``."""
        route.route_id = self.meta.route_id
        self._routes.appendleft(route)

    def number_remaining_routes(self) -> int:
        return len(self._routes)

    def current_route(self) -> Route | None:
        if self._current_route is None:
            self.next_route()
        return self._current_route

    def next_route(self) -> Route | None:
        self._current_route = self._routes.popleft() if self._routes else None
        return self._current_route

    def peek_at_next_route(self) -> Route | None:
        return self._routes[0] if self._routes else None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "type": self.TYPE,
            "meta": self.meta.to_dict(),
            "routes": [r.to_dict() for r in self._routes],
        }
        if self._current_route is not None:
            out["current_route"] = self._current_route.to_dict()
        return out

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DynamicRoutingSlip":
        raw_current = data.get("current_route")
        return cls(
            meta=RouteMeta.from_dict(data.get("meta", {})),
            routes=[route_from_dict(r) for r in data.get("routes", [])],
            current_route=route_from_dict(raw_current) if raw_current else None,
        )
