"""Ports ``ra.common.file.Multipart`` - a ``multipart/form-data`` body builder.

Like the Java version (whose HTTP transport was commented out) this only
accumulates the body string; sending it is the caller's concern. ``FileUtil``,
``InfoVault*`` and the secure-file wrappers are deferred.
"""

from __future__ import annotations

from typing import Any

from ._serde import compact
from .util.random_util import random_alphanumeric

_LINE_FEED = "\r\n"


class Multipart:
    """Accumulates a ``multipart/form-data`` request body."""

    def __init__(self, charset: str | None = None, boundary: str | None = None) -> None:
        self.boundary = boundary or random_alphanumeric(32)
        self.charset = charset
        self._body = ""

    def add_form_field(self, name: str, value: str) -> None:
        charset = self.charset or "UTF-8"
        self._body += f"--{self.boundary}{_LINE_FEED}"
        self._body += f'Content-Disposition: form-data; name="{name}"{_LINE_FEED}'
        self._body += f"Content-Type: text/plain; charset={charset}{_LINE_FEED}{_LINE_FEED}"
        self._body += value + _LINE_FEED

    def add_file_part(self, field_name: str, file_name: str | None = None) -> None:
        self._body += f"--{self.boundary}{_LINE_FEED}"
        if file_name is not None:
            self._body += f'Content-Disposition: file; filename="{file_name}"{_LINE_FEED}'
        else:
            self._body += f'Content-Disposition: file; name="{field_name}";{_LINE_FEED}'
        self._body += f"Content-Type: application/octet-stream{_LINE_FEED}"
        self._body += f"Content-Transfer-Encoding: binary{_LINE_FEED}{_LINE_FEED}"

    def add_header_field(self, name: str, value: str) -> None:
        self._body += f"{name}: {value}{_LINE_FEED}"

    def append_raw(self, text: str) -> None:
        self._body += text

    def body(self) -> str:
        return self._body

    def finish(self) -> str:
        return self._body + f"--{self.boundary}--{_LINE_FEED}"

    def to_dict(self) -> dict[str, Any]:
        return {"boundary": self.boundary, **compact({"charset": self.charset})}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Multipart":
        return cls(charset=data.get("charset"), boundary=data.get("boundary"))
