"""Ports ``ra.common.crypto.EncryptionAlgorithm``."""

from __future__ import annotations

from enum import Enum

from ..errors import InvalidInput


class EncryptionAlgorithm(str, Enum):
    """Symmetric encryption algorithm label.

    These are just identifiers carried in :class:`ra_common.content.Content`
    metadata; this package does not encrypt.
    """

    CAST5 = "Cast5"
    AES256 = "Aes256"
    AES512 = "Aes512"

    @property
    def wire_name(self) -> str:
        return {
            EncryptionAlgorithm.CAST5: "CAST-5",
            EncryptionAlgorithm.AES256: "AES-256",
            EncryptionAlgorithm.AES512: "AES-512",
        }[self]

    @classmethod
    def parse(cls, text: str) -> "EncryptionAlgorithm":
        table = {
            "CAST-5": cls.CAST5, "Cast5": cls.CAST5,
            "AES-256": cls.AES256, "Aes256": cls.AES256,
            "AES-512": cls.AES512, "Aes512": cls.AES512,
        }
        try:
            return table[text]
        except KeyError:
            raise InvalidInput(f"unknown encryption algorithm: {text}") from None
