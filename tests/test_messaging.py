from ra_common.messaging import (
    Command,
    CommandMessage,
    DocumentMessage,
    EventMessage,
    EventType,
    TextMessage,
    message_from_dict,
)


def test_tagged_round_trip():
    for msg in (
        DocumentMessage(),
        CommandMessage(Command.START),
        EventMessage.of(EventType.SERVICE_STATUS),
        TextMessage(),
    ):
        data = msg.to_dict()
        assert "kind" in data
        back = message_from_dict(data)
        assert type(back) is type(msg)


def test_error_messages_shared_api():
    msg = CommandMessage(Command.REPORT)
    msg.add_error_message("boom")
    assert msg.error_messages == ["boom"]
    msg.clear_error_messages()
    assert msg.error_messages == []


def test_document_primary_bucket():
    d = DocumentMessage()
    assert len(d.data) == 1
    d.put("k", 1)
    assert d.get("k") == 1


def test_command_wire_value():
    assert CommandMessage(Command.GRACEFULLY_SHUTDOWN).to_dict()["command"] == "GracefullyShutdown"
