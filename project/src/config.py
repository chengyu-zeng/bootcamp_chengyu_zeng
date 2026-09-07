"""Configuration helpers for the integrated SPY risk-alert project."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"


def load_env(env_file: str | Path | None = None, *, override: bool = False) -> bool:
    """Load a local environment file without relying on the launch directory."""

    target = Path(env_file).expanduser() if env_file is not None else DEFAULT_ENV_FILE
    return load_dotenv(dotenv_path=target, override=override)


def get_key(name: str, default: str | None = None, *, required: bool = False) -> str | None:
    """Return one configuration value and optionally require a non-empty value."""

    value = os.getenv(name, default)
    if required and not value:
        raise KeyError(f"Required environment variable is missing: {name}")
    return value


def get_data_dir() -> Path:
    """Resolve DATA_DIR relative to the project root when it is not absolute."""

    return get_path_from_env("DATA_DIR", "./data")


def get_path_from_env(name: str, default: str) -> Path:
    """Resolve one configured path relative to the project root when needed."""

    configured = Path(get_key(name, default) or default).expanduser()
    if not configured.is_absolute():
        configured = PROJECT_ROOT / configured
    return configured.resolve()


def get_raw_data_dir() -> Path:
    """Return the configured directory for immutable source snapshots."""

    return get_path_from_env("DATA_DIR_RAW", "data/raw")


def get_processed_data_dir() -> Path:
    """Return the configured directory for reproducible derived data."""

    return get_path_from_env("DATA_DIR_PROCESSED", "data/processed")
