"""Tiny JSON (de)serialization helpers shared across the package.

``ra-common-python`` deliberately takes no third-party dependencies, so there is
no pydantic / attrs here. Every serializable type exposes ``to_dict()`` and a
``from_dict()`` classmethod; this module just wraps them in ``to_json`` /
``from_json`` and provides small utilities for the common patterns (skip
``None`` fields, encode/decode enums, base64 bytes).

Serialization is **not** wire-compatible with ``ra-common-java`` (which used a
hand-rolled JSON layer and reflective polymorphism).
"""

from __future__ import annotations

import base64
import json
from enum import Enum
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Serializable(Protocol):
    def to_dict(self) -> dict[str, Any]: ...

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Any: ...


def compact(data: dict[str, Any]) -> dict[str, Any]:
    """Drop keys whose value is ``None`` (mirrors serde ``skip_serializing_if``)."""
    return {k: v for k, v in data.items() if v is not None}


def enum_value(value: Enum | None) -> Any:
    return None if value is None else value.value


def b64encode(data: bytes | None) -> str | None:
    return None if data is None else base64.b64encode(data).decode("ascii")


def b64decode(text: str | None) -> bytes | None:
    return None if text is None else base64.b64decode(text)


def to_json(obj: Serializable, *, indent: int | None = 2) -> str:
    return json.dumps(obj.to_dict(), indent=indent, sort_keys=False)


def from_json(cls: type, text: str) -> Any:
    return cls.from_dict(json.loads(text))
