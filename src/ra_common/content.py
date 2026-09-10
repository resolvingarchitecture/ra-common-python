"""Typed content submitted to the network for dissemination.

Ports ``ra.common.content.Content`` and its subclasses (``Text``, ``HTML``,
``JSON``, ``Binary``, ``Image``, ``Audio``, ``Video``). The Java class hierarchy
collapses into one :class:`Content` dataclass tagged with a :class:`ContentKind`.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ._serde import b64decode, b64encode, compact
from .crypto import hash_util
from .crypto.encryption import EncryptionAlgorithm
from .crypto.hash import Hash, HashAlgorithm
from .errors import InvalidInput
from .util.random_util import random_alphanumeric


class ContentKind(str, Enum):
    TEXT = "Text"
    HTML = "Html"
    JSON = "Json"
    IMAGE = "Image"
    AUDIO = "Audio"
    VIDEO = "Video"
    BINARY = "Binary"

    @classmethod
    def for_content_type(cls, content_type: str) -> "ContentKind | None":
        if content_type.startswith("text/plain"):
            return cls.TEXT
        if content_type.startswith("text/html"):
            return cls.HTML
        if content_type.startswith("application/json"):
            return cls.JSON
        if content_type.startswith("image/"):
            return cls.IMAGE
        if content_type.startswith("audio/"):
            return cls.AUDIO
        if content_type.startswith("video/"):
            return cls.VIDEO
        return None

    def is_text(self) -> bool:
        return self in (ContentKind.TEXT, ContentKind.HTML, ContentKind.JSON)


@dataclass
class Content:
    """A unit of content plus its metadata (hashes, encryption info, keywords, a
    child tree)."""

    kind: ContentKind
    content_type: str
    version: int = 0
    id: str | None = None
    label: str | None = None
    name: str | None = None
    location: str | None = None
    size: int = 0
    author_alias: str | None = None
    author_address: str | None = None
    body: bytes | None = None
    body_encoding: str | None = None
    body_base64_encoded: bool = False
    created_at: int | None = None
    hash: Hash | None = None
    hash_algorithm: HashAlgorithm = HashAlgorithm.SHA256
    fingerprint: Hash | None = None
    fingerprint_algorithm: HashAlgorithm = HashAlgorithm.SHA1
    children: list["Content"] = field(default_factory=list)
    encrypted: bool = False
    encryption_algorithm: EncryptionAlgorithm | None = None
    encryption_passphrase: str | None = None
    encryption_passphrase_encrypted: bool = False
    encryption_passphrase_algorithm: EncryptionAlgorithm | None = None
    base64_encoded_iv: str | None = None
    keywords: list[str] = field(default_factory=list)
    readable: bool = False
    writeable: bool = False

    @classmethod
    def build(
        cls,
        body: bytes,
        content_type: str,
        label: str | None = None,
        name: str | None = None,
        generate_hash: bool = False,
        generate_fingerprint: bool = False,
    ) -> "Content":
        """Build content from a body and MIME type. Ports ``Content.buildContent``."""
        kind = ContentKind.for_content_type(content_type)
        if kind is None:
            raise InvalidInput(f"unsupported content type: {content_type}")
        c = cls(kind=kind, content_type=content_type, label=label, name=name)
        if "charset:" in content_type:
            c.body_encoding = content_type.split("charset:", 1)[1]
        c.set_body(body, generate_hash, generate_fingerprint)
        c.created_at = int(time.time() * 1000)
        c.id = random_alphanumeric(32)
        return c

    def set_body(
        self, body: bytes, generate_hash: bool = False, generate_fingerprint: bool = False
    ) -> None:
        self.size = len(body)
        if generate_hash:
            self.hash = Hash(
                hash_util.generate_hash(body, self.hash_algorithm), self.hash_algorithm
            )
        if generate_fingerprint and self.hash is not None:
            fp = hash_util.generate_fingerprint(
                self.hash.hash.encode("utf-8"), self.fingerprint_algorithm
            )
            self.fingerprint = Hash(fp, self.fingerprint_algorithm)
        self.body = body
        self.version += 1

    def meta_only(self) -> bool:
        return self.body is None

    def add_keyword(self, keyword: str) -> None:
        self.keywords.append(keyword)

    def add_child(self, child: "Content") -> None:
        self.children.append(child)

    def magnet_link(self) -> str | None:
        parts: list[str] = []
        if self.body is not None:
            parts.append(f"xl={len(self.body)}")
        if self.hash is not None:
            parts.append(f"xt=urn:{self.hash.algorithm.jca_name.lower()}:{self.hash.hash}")
        if self.keywords:
            parts.append(f"kt={'+'.join(self.keywords)}")
        return f"magnet:?{'&'.join(parts)}" if parts else None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "type": self.kind.value,
            "content_type": self.content_type,
            "version": self.version,
            **compact(
                {
                    "id": self.id,
                    "label": self.label,
                    "name": self.name,
                    "location": self.location,
                    "author_alias": self.author_alias,
                    "author_address": self.author_address,
                    "body": b64encode(self.body),
                    "body_encoding": self.body_encoding,
                    "created_at": self.created_at,
                    "hash": self.hash.to_dict() if self.hash else None,
                    "fingerprint": self.fingerprint.to_dict() if self.fingerprint else None,
                    "encryption_algorithm": (
                        self.encryption_algorithm.value if self.encryption_algorithm else None
                    ),
                    "encryption_passphrase": self.encryption_passphrase,
                    "encryption_passphrase_algorithm": (
                        self.encryption_passphrase_algorithm.value
                        if self.encryption_passphrase_algorithm
                        else None
                    ),
                    "base64_encoded_iv": self.base64_encoded_iv,
                }
            ),
            "size": self.size,
            "body_base64_encoded": self.body_base64_encoded,
            "hash_algorithm": self.hash_algorithm.value,
            "fingerprint_algorithm": self.fingerprint_algorithm.value,
            "encrypted": self.encrypted,
            "encryption_passphrase_encrypted": self.encryption_passphrase_encrypted,
            "readable": self.readable,
            "writeable": self.writeable,
        }
        if self.children:
            out["children"] = [c.to_dict() for c in self.children]
        if self.keywords:
            out["keywords"] = list(self.keywords)
        return out

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Content":
        def _enc(v: Any) -> EncryptionAlgorithm | None:
            return EncryptionAlgorithm(v) if v else None

        return cls(
            kind=ContentKind(data["type"]),
            content_type=data["content_type"],
            version=data.get("version", 0),
            id=data.get("id"),
            label=data.get("label"),
            name=data.get("name"),
            location=data.get("location"),
            size=data.get("size", 0),
            author_alias=data.get("author_alias"),
            author_address=data.get("author_address"),
            body=b64decode(data.get("body")),
            body_encoding=data.get("body_encoding"),
            body_base64_encoded=data.get("body_base64_encoded", False),
            created_at=data.get("created_at"),
            hash=Hash.from_dict(data["hash"]) if data.get("hash") else None,
            hash_algorithm=HashAlgorithm(data.get("hash_algorithm", HashAlgorithm.SHA256.value)),
            fingerprint=Hash.from_dict(data["fingerprint"]) if data.get("fingerprint") else None,
            fingerprint_algorithm=HashAlgorithm(
                data.get("fingerprint_algorithm", HashAlgorithm.SHA1.value)
            ),
            children=[cls.from_dict(c) for c in data.get("children", [])],
            encrypted=data.get("encrypted", False),
            encryption_algorithm=_enc(data.get("encryption_algorithm")),
            encryption_passphrase=data.get("encryption_passphrase"),
            encryption_passphrase_encrypted=data.get("encryption_passphrase_encrypted", False),
            encryption_passphrase_algorithm=_enc(data.get("encryption_passphrase_algorithm")),
            base64_encoded_iv=data.get("base64_encoded_iv"),
            keywords=list(data.get("keywords", [])),
            readable=data.get("readable", False),
            writeable=data.get("writeable", False),
        )
