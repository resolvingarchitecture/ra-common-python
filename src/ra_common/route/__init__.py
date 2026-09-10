"""Routing: routes, routing slips and external/relayed routes.

Ports the ``ra.common.route`` package.
"""

from __future__ import annotations

from .external import RelayedExternalRoute, SimpleExternalRoute, external_status
from .model import Route, RouteMeta, SimpleRoute, route_from_dict
from .slip import DynamicRoutingSlip

__all__ = [
    "Route",
    "RouteMeta",
    "SimpleRoute",
    "route_from_dict",
    "DynamicRoutingSlip",
    "SimpleExternalRoute",
    "RelayedExternalRoute",
    "external_status",
]
