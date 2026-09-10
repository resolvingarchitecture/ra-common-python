from ra_common import Envelope
from ra_common.envelope import HEADER_CONTENT_TYPE_JSON
from ra_common.messaging import CommandMessage, DocumentMessage, EventMessage, EventType


def test_factories_set_message_kind():
    assert isinstance(Envelope.document().message, DocumentMessage)
    assert isinstance(Envelope.command().message, CommandMessage)
    assert isinstance(Envelope.event(EventType.BUS_STATUS).message, EventMessage)
    assert Envelope.headers_only().message is None


def test_content_round_trips_through_document():
    e = Envelope.document()
    assert e.add_content("hello")
    assert e.content() == "hello"

    cmd = Envelope.command()
    assert not cmd.add_content(None)


def test_exceptions_accumulate():
    e = Envelope.document()
    e.add_exception("first")
    e.add_exception("second")
    assert e.exceptions() == ["first", "second"]


def test_ratchet_walks_the_slip_lifo():
    e = Envelope.document()
    e.add_route("ra.a.ServiceA", "OP")
    e.add_route("ra.b.ServiceB", "OP")
    e.ratchet()
    assert e.route.service == "ra.b.ServiceB"
    e.ratchet()
    assert e.route.service == "ra.a.ServiceA"


def test_json_round_trip():
    e = Envelope.document()
    e.set_content_type(HEADER_CONTENT_TYPE_JSON)
    e.add_content(42)
    e.add_route("ra.x.Svc", "DO")
    e.mark("seen")
    back = Envelope.from_json(e.to_json())
    assert back.id == e.id
    assert back.content_type() == HEADER_CONTENT_TYPE_JSON
    assert back.content() == 42
    assert back.marker_present("seen")
    assert back.dynamic_routing_slip.number_remaining_routes() == 1


def test_equality_is_by_id():
    assert Envelope.document_with_id("same") == Envelope.document_with_id("same")


def test_error_messages():
    e = Envelope.command()
    e.add_error_message("boom")
    assert e.error_messages() == ["boom"]
