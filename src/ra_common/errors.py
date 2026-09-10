"""Package-wide error type.

Replaces the family of checked ``*Exception`` classes in ``ra-common-java``
(``ServiceNotFoundException``, ``FileCreationFailedException``, ...).
"""

from __future__ import annotations


class RaError(Exception):
    """Base class for everything that can go wrong in ``ra_common``."""


class DecodeError(RaError):
    """A string could not be decoded from its expected encoding (base32/58/hex/base64)."""


class CryptoError(RaError):
    """A cryptographic operation failed or verification did not pass."""


class InvalidInput(RaError):
    """A malformed value was supplied (bad HashCash token, bad multihash, ...)."""


class ServiceNotFound(RaError):
    """A named service could not be found."""


class ServiceNotAccessible(RaError):
    """A service is registered but not reachable."""


class ServiceNotSupported(RaError):
    """A service type is not supported by this runtime."""


class ServiceAlreadyRegistered(RaError):
    """A service with this identity is already registered."""


class FileCreationFailed(RaError):
    """A file or directory could not be created."""
