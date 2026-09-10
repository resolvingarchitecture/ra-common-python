"""ra-common: foundational types for the Resolving Architecture / 1M5 ecosystem.

A Python port of `ra-common-java <https://github.com/resolvingarchitecture/ra-common-java>`_.
Serialization is JSON-based and **not** wire-compatible with the Java library
(which used a hand-rolled JSON layer and reflective polymorphism).

Phase 1 scope: :mod:`~ra_common.envelope`, :mod:`~ra_common.messaging`,
:mod:`~ra_common.route`, :mod:`~ra_common.service`, :mod:`~ra_common.identity`,
:mod:`~ra_common.crypto`, :mod:`~ra_common.content`, :mod:`~ra_common.tasks`,
:mod:`~ra_common.config`, a minimal :mod:`~ra_common.network` slice, and
:mod:`~ra_common.util`.
"""

from __future__ import annotations

from . import config, crypto, encoding, errors, util
from .content import Content, ContentKind
from .envelope import Action, Envelope, MessageType
from .errors import RaError
from .file import Multipart
from .identity import Did, PublicKey, Signature
from .lifecycle import Client, LifeCycle, Status
from .messaging import (
    Command,
    CommandMessage,
    DocumentMessage,
    EventMessage,
    EventType,
    Message,
    MessageBus,
    MessageChannel,
    MessageConsumer,
    MessageProducer,
    TextMessage,
)
from .network import Network, NetworkPeer, NetworkStatus
from .route import DynamicRoutingSlip, Route, SimpleRoute
from .service import (
    Service,
    ServiceCore,
    ServiceLevel,
    ServiceReport,
    ServiceStatus,
)
from .tasks import Task, TaskConfig, TaskRunner

__version__ = "0.1.0"

__all__ = [
    "config",
    "crypto",
    "encoding",
    "errors",
    "util",
    "Content",
    "ContentKind",
    "Action",
    "Envelope",
    "MessageType",
    "RaError",
    "Multipart",
    "Did",
    "PublicKey",
    "Signature",
    "Client",
    "LifeCycle",
    "Status",
    "Command",
    "CommandMessage",
    "DocumentMessage",
    "EventMessage",
    "EventType",
    "Message",
    "MessageBus",
    "MessageChannel",
    "MessageConsumer",
    "MessageProducer",
    "TextMessage",
    "Network",
    "NetworkPeer",
    "NetworkStatus",
    "DynamicRoutingSlip",
    "Route",
    "SimpleRoute",
    "Service",
    "ServiceCore",
    "ServiceLevel",
    "ServiceReport",
    "ServiceStatus",
    "Task",
    "TaskConfig",
    "TaskRunner",
    "__version__",
]
