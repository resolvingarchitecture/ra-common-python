"""Minimal network identity types needed by :mod:`ra_common.route` and
:mod:`ra_common.envelope`.

Ports ``ra.common.network.Network``, ``NetworkStatus`` and ``NetworkPeer``. The
full network service layer is deferred to a later phase.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ._serde import compact
from .identity import Did


class Network(str, Enum):
    CARD = "Card"
    NFC = "Nfc"
    HTTP = "Http"
    TOR = "Tor"
    I2P = "I2p"
    WIFI = "WiFi"
    BLUETOOTH = "Bluetooth"
    SATELLITE = "Satellite"
    FS_RADIO = "FsRadio"
    LI_FI = "LiFi"


class NetworkStatus(str, Enum):
    NOT_INSTALLED = "NotInstalled"
    CLOSED = "Closed"
    ERROR = "Error"
    PORT_CONFLICT = "PortConflict"
    WAITING = "Waiting"
    WARMUP = "Warmup"
    CONNECTING = "Connecting"
    CONNECTED = "Connected"
    VERIFIED = "Verified"
    HANGING = "Hanging"
    FAILED = "Failed"
    BLOCKED = "Blocked"
    DISCONNECTED = "Disconnected"


@dataclass
class NetworkPeer:
    """A peer in a peer-to-peer network, identified by :class:`Did` and :class:`Network`.

    Equality follows the Java version: two peers are equal iff both have a
    public-key address and fingerprint and both match.
    """

    network: Network = Network.HTTP
    did: Did = field(default_factory=Did)
    id: str | None = None
    port: int | None = None
    services: list[str] = field(default_factory=list)

    @classmethod
    def with_credentials(
        cls, network: Network, username: str, passphrase: str | None = None
    ) -> "NetworkPeer":
        did = Did.with_username(username)
        did.passphrase = passphrase
        return cls(network=network, did=did)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NetworkPeer):
            return NotImplemented
        a = _peer_key(self)
        b = _peer_key(other)
        return a is not None and a == b

    def __hash__(self) -> int:
        return hash(_peer_key(self))

    def to_dict(self) -> dict[str, Any]:
        return {
            **compact({"id": self.id, "port": self.port}),
            "network": self.network.value,
            "did": self.did.to_dict(),
            **({"services": list(self.services)} if self.services else {}),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NetworkPeer":
        return cls(
            network=Network(data.get("network", Network.HTTP.value)),
            did=Did.from_dict(data.get("did", {})),
            id=data.get("id"),
            port=data.get("port"),
            services=list(data.get("services", [])),
        )


def _peer_key(peer: NetworkPeer) -> tuple[str, str] | None:
    pk = peer.did.public_key
    if pk.address is not None and pk.fingerprint is not None:
        return (pk.address, pk.fingerprint)
    return None
