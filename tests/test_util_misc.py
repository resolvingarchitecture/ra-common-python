import pytest

from ra_common import config
from ra_common.content import Content, ContentKind
from ra_common.encoding import base32_decode, base32_encode, base58_decode, base58_encode
from ra_common.errors import DecodeError, InvalidInput
from ra_common.file import Multipart
from ra_common.network import Network, NetworkPeer
from ra_common.util import (
    Nonce,
    UniqueId,
    capitalize,
    capitalize_first,
    pack_big_endian,
    unpack_big_endian,
    version_compare,
)


def test_bytes_round_trip():
    for v in (0, 1, -1, 42, -(2**31), 2**31 - 1, 0x0A0B0C0D):
        assert pack_big_endian(unpack_big_endian(v)) == v
    assert unpack_big_endian(0x01020304) == bytes([1, 2, 3, 4])


def test_strings():
    assert capitalize_first("abc def") == "Abc def"
    assert capitalize("one two three") == "One Two Three"


def test_version_compare():
    assert version_compare("1.8", "1.11") == -1
    assert version_compare("2.0", "2.0") == 0
    assert version_compare("2.0", "2.0.0") == -1
    assert version_compare("8ea", "8") == 0
    assert version_compare("8-ea", "8") == 1
    assert version_compare("1.8.0_275", "1.8.0_271") == 1


def test_nonce_rejects_replays():
    n = Nonce()
    assert n.continue_on(1)
    assert n.continue_on(2)
    assert not n.continue_on(1)
    assert len(n) == 2


def test_nonce_prunes_oldest():
    n = Nonce(max_size=4, prune_percent=50)
    for i in range(5):
        n.continue_on(i)
    n.continue_on(100)
    assert n.continue_on(0)


def test_unique_id_base64_round_trip():
    uid = UniqueId.random()
    s = uid.to_base64()
    assert len(s) == 44
    assert UniqueId.from_base64(s) == uid
    assert UniqueId(bytes(32)) < UniqueId(bytes([0xFF] * 32))
    assert UniqueId.from_slice(b"\x00" * 8 + bytes([7] * 32), 8).as_bytes() == bytes([7] * 32)


def test_encoding():
    data = b"resolving architecture"
    assert base32_decode(base32_encode(data)) == data
    assert base58_encode(b"Hello World!") == "2NEpo7TZRRrLZSi2U"
    assert base58_decode("2NEpo7TZRRrLZSi2U") == b"Hello World!"
    with pytest.raises(DecodeError):
        base58_decode("0OIl")


def test_content_build_and_magnet():
    c = Content.build(b"hello", "text/plain", name="greeting", generate_hash=True, generate_fingerprint=True)
    assert c.kind is ContentKind.TEXT
    assert c.size == 5 and c.version == 1
    assert c.id and c.hash and c.fingerprint
    with pytest.raises(InvalidInput):
        Content.build(b"", "application/x-tar")

    b = Content(ContentKind.BINARY, "application/octet-stream")
    b.set_body(bytes([1, 2, 3, 4]), generate_hash=True)
    b.add_keyword("alpha")
    b.add_keyword("beta")
    m = b.magnet_link()
    assert m.startswith("magnet:?xl=4")
    assert "kt=alpha+beta" in m

    back = Content.from_dict(c.to_dict())
    assert back.kind is ContentKind.TEXT
    assert back.body == b"hello"


def test_network_peer():
    a = NetworkPeer(Network.TOR)
    b = NetworkPeer(Network.TOR)
    assert a != b
    for p in (a, b):
        p.did.public_key.address = "addr"
        p.did.public_key.fingerprint = "fp"
    assert a == b
    back = NetworkPeer.from_dict(a.to_dict())
    assert back.network is Network.TOR


def test_multipart():
    m = Multipart("UTF-8")
    m.add_form_field("a", "1")
    boundary = m.boundary
    out = m.finish()
    assert f"--{boundary}" in out
    assert 'name="a"' in out
    assert out.rstrip().endswith(f"--{boundary}--")


def test_config_parsing():
    p = config.load_from_args(["a=1", "b=2", "ignored"])
    assert p == {"a": "1", "b": "2"}
    props = config.parse_properties("# comment\nra.version = 1.2.0\n\nx = y = z\n")
    assert props["ra.version"] == "1.2.0"
    assert props["x"] == "y = z"
