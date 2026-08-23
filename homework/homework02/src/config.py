"""Environment configuration helpers for the Stage 02 workspace."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


HOMEWORK_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_FILE = HOMEWORK_ROOT / ".env"


def load_env(env_file: str | Path | None = None, *, override: bool = False) -> bool:
    """Load environment variables from an explicit file.

    The default is the .env file at the root of homework02, so behavior does
    not depend on the directory from which Python or Jupyter was launched.
    """

    target = Path(env_file).expanduser() if env_file is not None else DEFAULT_ENV_FILE
    return load_dotenv(dotenv_path=target, override=override)


def get_key(name: str, default: str | None = None, *, required: bool = False) -> str | None:
    """Return one environment value and optionally require a non-empty result."""

    value = os.getenv(name, default)
    if required and not value:
        raise KeyError(f"Required environment variable is missing: {name}")
    return value


def get_data_dir() -> Path:
    """Resolve DATA_DIR relative to the homework root when it is not absolute."""

    configured = Path(get_key("DATA_DIR", "./data") or "./data").expanduser()
    if not configured.is_absolute():
        configured = HOMEWORK_ROOT / configured
    return configured.resolve()
