"""Configuration loading and cross-platform directory resolution.

Ports ``ra.common.Config`` and ``ra.common.SystemSettings``. Environment
variables and a ``.properties`` / ``.config`` file are the sources.
"""

from __future__ import annotations

import os
from pathlib import Path

from .errors import FileCreationFailed


def load_from_args(args: list[str], delimiter: str = "=") -> dict[str, str]:
    """Parse ``key<delimiter>value`` arguments. Arguments without the delimiter
    are ignored (matching the Java behaviour)."""
    out: dict[str, str] = {}
    for arg in args:
        key, sep, value = arg.partition(delimiter)
        if sep:
            out[key] = value
    return out


def load_from_env() -> dict[str, str]:
    """Snapshot the process environment."""
    return dict(os.environ)


def parse_properties(text: str) -> dict[str, str]:
    """Parse ``.properties``-style text: ``key=value`` lines, ``#``/``!`` comments."""
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("!"):
            continue
        for sep in ("=", ":"):
            if sep in line:
                key, _, value = line.partition(sep)
                out[key.strip()] = value.strip()
                break
    return out


def load_from_file(path: str | os.PathLike[str]) -> dict[str, str]:
    """Load a ``.properties`` / ``.config`` file."""
    return parse_properties(Path(path).read_text())


def load_all(
    client_props: dict[str, str], config_path: str | os.PathLike[str] | None = None
) -> dict[str, str]:
    """Merge sources with increasing precedence: environment, then the optional
    config file, then ``client_props``."""
    config = load_from_env()
    if config_path is not None:
        config.update(load_from_file(config_path))
    config.update(client_props)
    return config


class SystemSettings:
    """XDG-style, cross-platform application directory resolution. Ports
    ``ra.common.SystemSettings``."""

    @staticmethod
    def user_home_dir() -> Path | None:
        home = os.environ.get("HOME") or os.environ.get("USERPROFILE")
        return Path(home) if home else None

    @classmethod
    def _xdg_dir(cls, env_key: str, default_suffix: str) -> Path | None:
        value = os.environ.get(env_key)
        if value:
            return Path(value)
        home = cls.user_home_dir()
        return home / default_suffix if home else None

    @classmethod
    def user_data_dir(cls) -> Path | None:
        return cls._xdg_dir("XDG_DATA_HOME", ".local/share")

    @classmethod
    def user_config_dir(cls) -> Path | None:
        return cls._xdg_dir("XDG_CONFIG_HOME", ".config")

    @classmethod
    def user_cache_dir(cls) -> Path | None:
        return cls._xdg_dir("XDG_CACHE_HOME", ".cache")

    @staticmethod
    def app_dir(base: Path, group: str, app: str, create: bool = False) -> Path:
        directory = base / group / app
        if create and not directory.exists():
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                raise FileCreationFailed(f"{directory}: {exc}") from exc
        return directory

    @classmethod
    def user_app_data_dir(cls, group: str, app: str, create: bool = False) -> Path:
        base = cls.user_data_dir()
        if base is None:
            raise FileCreationFailed("no user data dir")
        return cls.app_dir(base, group, app, create)

    @classmethod
    def user_app_config_dir(cls, group: str, app: str, create: bool = False) -> Path:
        base = cls.user_config_dir()
        if base is None:
            raise FileCreationFailed("no user config dir")
        return cls.app_dir(base, group, app, create)

    @classmethod
    def user_app_cache_dir(cls, group: str, app: str, create: bool = False) -> Path:
        base = cls.user_cache_dir()
        if base is None:
            raise FileCreationFailed("no user cache dir")
        return cls.app_dir(base, group, app, create)
