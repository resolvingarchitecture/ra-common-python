"""Ports ``ra.common.messaging.CommandMessage``."""

from __future__ import annotations

from enum import Enum
from typing import Any

from .message import Message


class Command(str, Enum):
    """A command for a service to execute. Ports ``CommandMessage.Command``."""

    START = "Start"
    SHUTDOWN = "Shutdown"
    GRACEFULLY_SHUTDOWN = "GracefullyShutdown"
    RESTART = "Restart"
    PAUSE = "Pause"
    UNPAUSE = "Unpause"
    NET_STATE = "NetState"
    REPORT = "Report"
    REGISTER_STATE_CHANGE_LISTENER = "RegisterStateChangeListener"
    UNREGISTER_STATE_CHANGE_LISTENER = "UnregisterStateChangeListener"


class CommandMessage(Message):
    """A message telling a service which :class:`Command` to run."""

    KIND = "command"

    def __init__(
        self,
        command: Command | None = None,
        error_messages: list[str] | None = None,
    ) -> None:
        self.error_messages = error_messages or []
        self.command = command

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"kind": self.KIND}
        if self.command is not None:
            out["command"] = self.command.value
        if self.error_messages:
            out["error_messages"] = list(self.error_messages)
        return out

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CommandMessage":
        raw = data.get("command")
        return cls(
            command=Command(raw) if raw is not None else None,
            error_messages=list(data.get("error_messages", [])),
        )
