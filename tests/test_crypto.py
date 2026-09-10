import pytest

from ra_common.crypto import Hash, HashAlgorithm, HashCash, Multihash, MultihashType
from ra_common.crypto import hash_util
from ra_common.crypto.hashcash import _leading_zero_bits
from ra_common.errors import InvalidInput


def test_hash_equality_is_on_string():
    assert Hash("abc", HashAlgorithm.SHA256) == Hash("abc", HashAlgorithm.SHA1)


def test_hash_algorithm_names():
    assert HashAlgorithm.SHA256.jca_name == "SHA-256"
    assert HashAlgorithm.parse("PBKDF2WithHmacSHA1") is HashAlgorithm.PBKDF2_HMAC_SHA1


def test_hex_grouping():
    assert hash_util.to_hex(bytes([0x0A, 0x0B, 0x0C, 0x0D, 0x1E])) == "0A0B:0C0D:1E"
    assert hash_util.from_hex("0A0B:0C0D:1E") == bytes([0x0A, 0x0B, 0x0C, 0x0D, 0x1E])


def test_salted_hash_round_trip():
    h = hash_util.generate_hash(b"Alice", HashAlgorithm.SHA256)
    assert hash_util.verify_hash(b"Alice", h, HashAlgorithm.SHA256)
    assert not hash_util.verify_hash(b"Bob", h, HashAlgorithm.SHA256)


def test_password_hash_round_trip():
    h = hash_util.generate_password_hash("hunter2")
    assert h.startswith("1000_")
    assert hash_util.verify_password_hash("hunter2", h)
    assert not hash_util.verify_password_hash("hunter3", h)


def test_password_hash_via_generate_hash():
    h = hash_util.generate_hash(b"pw", HashAlgorithm.PBKDF2_HMAC_SHA1)
    assert hash_util.verify_hash(b"pw", h, HashAlgorithm.PBKDF2_HMAC_SHA1)


def test_multihash_bytes_round_trip():
    m = Multihash(MultihashType.SHA2_256, bytes([0xAB] * 32))
    data = m.to_bytes()
    assert data[0] == 0x12 and data[1] == 32
    assert Multihash.from_bytes(data) == m
    assert Multihash.from_hex(m.to_hex()) == m
    assert Multihash.from_base58(m.to_base58()) == m


def test_multihash_length_validated():
    with pytest.raises(InvalidInput):
        Multihash(MultihashType.SHA1, bytes(10))
    with pytest.raises(InvalidInput):
        MultihashType.from_code(0x99)


def test_hashcash_mint_then_verify():
    hc = HashCash.mint("brian@resolvingarchitecture.io", 12)
    assert hc.computed_bits() >= 12
    assert hc.is_valid_for("brian@resolvingarchitecture.io", 12)
    assert not hc.is_valid_for("someone.else", 12)
    reparsed = HashCash.parse(hc.token)
    assert reparsed.resource == hc.resource
    assert reparsed.value >= 12


def test_hashcash_rejects_bad_shape():
    with pytest.raises(InvalidInput):
        HashCash.parse("9:bogus")
    with pytest.raises(InvalidInput):
        HashCash.parse("1:20:250101:res")
    with pytest.raises(InvalidInput):
        HashCash.mint("has:colon", 4)


def test_leading_zero_count():
    assert _leading_zero_bits(bytes([0x00, 0x00, 0x0F])) == 20
    assert _leading_zero_bits(bytes([0xFF])) == 0
    assert _leading_zero_bits(bytes([0x00, 0x00])) == 16
