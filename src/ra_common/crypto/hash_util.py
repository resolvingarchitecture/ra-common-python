"""Digests, fingerprints and passphrase hashing. Ports ``ra.common.HashUtil``.

Formats produced here (``b64(hash)_b64(salt)`` for salted digests,
``iterations_b64(salt)_b64(hash)`` for PBKDF2) mirror the Java layout but are
**this package's own format** - they are not required to interoperate with the
Java library.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

from ..errors import CryptoError, DecodeError, InvalidInput
from .hash import HashAlgorithm

_PBKDF2_ITERATIONS = 1000
_PBKDF2_KEY_LEN = 64
_SALT_LEN = 16

_DIGESTS = {
    HashAlgorithm.SHA1: "sha1",
    HashAlgorithm.SHA256: "sha256",
    HashAlgorithm.SHA512: "sha512",
}


def salt() -> bytes:
    """16 cryptographically-secure random salt bytes."""
    return secrets.token_bytes(_SALT_LEN)


def digest(data: bytes, algorithm: HashAlgorithm) -> bytes:
    """Raw digest of ``data`` with ``algorithm``."""
    name = _DIGESTS.get(algorithm)
    if name is None:
        raise CryptoError("PBKDF2 is not a plain digest")
    return hashlib.new(name, data).digest()


def to_hex(data: bytes) -> str:
    """Uppercase hex of ``data``, grouped into blocks of four chars by ``:``."""
    hexed = data.hex().upper()
    return ":".join(hexed[i:i + 4] for i in range(0, len(hexed), 4))


def from_hex(text: str) -> bytes:
    """Inverse of :func:`to_hex`; ``:`` separators are ignored."""
    clean = text.replace(":", "")
    try:
        return bytes.fromhex(clean)
    except ValueError as exc:
        raise DecodeError(str(exc)) from exc


def generate_fingerprint(data: bytes, algorithm: HashAlgorithm) -> str:
    """Fingerprint: the digest of ``data``, hex-encoded via :func:`to_hex`."""
    return to_hex(digest(data, algorithm))


def generate_hash(content: bytes, algorithm: HashAlgorithm) -> str:
    """Hash ``content``.

    For :attr:`HashAlgorithm.PBKDF2_HMAC_SHA1` this produces a passphrase hash;
    otherwise it salts and digests, returning ``b64(digest(salt + content))_b64(salt)``.
    """
    if algorithm is HashAlgorithm.PBKDF2_HMAC_SHA1:
        return generate_password_hash(content.decode("utf-8"))
    s = salt()
    h = digest(s + content, algorithm)
    return f"{base64.b64encode(h).decode()}_{base64.b64encode(s).decode()}"


def verify_hash(content: bytes, hash_to_verify: str, algorithm: HashAlgorithm) -> bool:
    """Verify ``content`` against a string produced by :func:`generate_hash`."""
    if algorithm is HashAlgorithm.PBKDF2_HMAC_SHA1:
        return verify_password_hash(content.decode("utf-8"), hash_to_verify)
    try:
        h_b64, s_b64 = hash_to_verify.split("_", 1)
    except ValueError:
        raise InvalidInput("malformed hash") from None
    try:
        expected = base64.b64decode(h_b64)
        s = base64.b64decode(s_b64)
    except Exception as exc:  # noqa: BLE001
        raise DecodeError(str(exc)) from exc
    actual = digest(s + content, algorithm)
    return hmac.compare_digest(actual, expected)


def generate_password_hash(password: str) -> str:
    """PBKDF2-HMAC-SHA1 passphrase hash: ``iterations_b64(salt)_b64(derived)``."""
    return _generate_password_hash_with_salt(password, salt())


def _generate_password_hash_with_salt(password: str, s: bytes) -> str:
    out = hashlib.pbkdf2_hmac(
        "sha1", password.encode("utf-8"), s, _PBKDF2_ITERATIONS, _PBKDF2_KEY_LEN
    )
    return f"{_PBKDF2_ITERATIONS}_{base64.b64encode(s).decode()}_{base64.b64encode(out).decode()}"


def verify_password_hash(password: str, hash_to_verify: str) -> bool:
    """Verify a passphrase against a string from :func:`generate_password_hash`."""
    parts = hash_to_verify.split("_")
    if len(parts) != 3:
        return False
    try:
        iterations = int(parts[0])
        s = base64.b64decode(parts[1])
        expected = base64.b64decode(parts[2])
    except (ValueError, Exception):  # noqa: BLE001
        return False
    out = hashlib.pbkdf2_hmac(
        "sha1", password.encode("utf-8"), s, iterations, len(expected)
    )
    return hmac.compare_digest(out, expected)
