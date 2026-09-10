from datetime import datetime, timezone

from ra_common.crypto import Hash, HashAlgorithm
from ra_common.identity import Did, DidStatus, DidType, PublicKey, Signature


def test_did_defaults_match_java():
    d = Did()
    assert d.username == "Anon"
    assert d.status is DidStatus.INACTIVE
    assert d.did_type is DidType.IDENTITY
    assert d.passphrase_hash_algorithm is HashAlgorithm.PBKDF2_HMAC_SHA1


def test_did_clear_sensitive():
    d = Did.with_username("alice")
    d.passphrase = "secret"
    d.authenticated = True
    d.clear_sensitive()
    assert d.username == ""
    assert d.passphrase is None
    assert d.status is DidStatus.PRIVATE
    assert not d.authenticated


def test_did_json_round_trip():
    d = Did.with_username("bob")
    d.public_key = PublicKey.from_address("addr")
    d.passphrase_hash = Hash("deadbeef", HashAlgorithm.SHA256)
    back = Did.from_dict(d.to_dict())
    assert back.username == "bob"
    assert back.public_key.address == "addr"
    assert back.passphrase_hash.hash == "deadbeef"


def test_signature_equality_on_address():
    a, b = Signature(), Signature()
    assert a != b
    a.signed_by_address = "addr1"
    b.signed_by_address = "addr1"
    assert a == b


def test_signature_json_round_trip():
    s = Signature(
        value_signed="hello",
        algorithm="Ed25519",
        signed_date=datetime.now(timezone.utc),
        signed_by_address="addr",
    )
    back = Signature.from_dict(s.to_dict())
    assert back.value_signed == "hello"
    assert back.signed_by_address == "addr"


def test_public_key_signed_attributes():
    pk = PublicKey.from_address("B32ADDR")
    pk.add_signed_attribute("email", Signature(signed_by_address="signer"))
    assert len(pk.signed_attributes["email"]) == 1
    pk.remove_signature("email", "signer")
    assert pk.signed_attributes["email"] == []
