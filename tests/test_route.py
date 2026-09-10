import json

from ra_common.route import DynamicRoutingSlip, SimpleRoute
from ra_common.route.model import route_from_dict


def test_lifo_walk():
    slip = DynamicRoutingSlip()
    slip.add_route(SimpleRoute.new("a", "op"))
    slip.add_route(SimpleRoute.new("b", "op"))
    slip.add_route(SimpleRoute.new("c", "op"))
    assert slip.number_remaining_routes() == 3
    assert slip.next_route().service == "c"
    assert slip.next_route().service == "b"
    assert slip.peek_at_next_route().service == "a"
    assert slip.next_route().service == "a"
    assert slip.next_route() is None


def test_add_route_stamps_route_id():
    slip = DynamicRoutingSlip()
    slip.add_route(SimpleRoute.new("a", "op"))
    assert slip.peek_at_next_route().route_id == slip.meta.route_id


def test_json_round_trip():
    slip = DynamicRoutingSlip()
    slip.add_route(SimpleRoute.new("a", "op"))
    from ra_common.route import SimpleExternalRoute

    slip.add_route(SimpleExternalRoute.new("b", "op"))
    back = DynamicRoutingSlip.from_dict(json.loads(json.dumps(slip.to_dict())))
    assert back.number_remaining_routes() == 2
    assert isinstance(route_from_dict(slip.to_dict()), DynamicRoutingSlip)
