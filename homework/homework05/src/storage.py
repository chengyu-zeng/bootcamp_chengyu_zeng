"""Environment-independent DataFrame storage utilities for Stage 05."""

from __future__ import annotations

import importlib.util
import uuid
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import pandas as pd

StorageFormat = Literal["csv", "parquet"]
PARQUET_SUFFIXES = {".parquet", ".parq", ".pq"}


def timestamp_utc(now: datetime | None = None) -> str:
    """Return a UTC timestamp suitable for Stage 05 filenames."""

    current = now or datetime.now(UTC)
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    return current.astimezone(UTC).strftime("%Y%m%d-%H%M")


def detect_format(path: str | Path) -> StorageFormat:
    """Return a supported storage format based on the path suffix."""

    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        return "csv"
    if suffix in PARQUET_SUFFIXES:
        return "parquet"
    supported = ".csv, .parquet, .parq, .pq"
    raise ValueError(f"Unsupported file suffix {suffix or '<none>'!r}; use {supported}")


def get_parquet_engine() -> str:
    """Return an installed pandas Parquet engine or raise an actionable error."""

    for engine in ("pyarrow", "fastparquet"):
        if importlib.util.find_spec(engine) is not None:
            return engine
    raise RuntimeError(
        "Parquet support is unavailable. Install an engine with "
        "`python -m pip install pyarrow` (recommended) or fastparquet."
    )


def write_df(
    frame: pd.DataFrame,
    path: str | Path,
    *,
    index: bool = False,
    parquet_compression: str = "snappy",
) -> Path:
    """Atomically write a DataFrame as CSV or Parquet based on its suffix."""

    if not isinstance(frame, pd.DataFrame):
        raise TypeError("frame must be a pandas DataFrame")

    destination = Path(path).expanduser()
    storage_format = detect_format(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(
        f".{destination.name}.{uuid.uuid4().hex}.temporary"
    )

    try:
        if storage_format == "csv":
            frame.to_csv(temporary, index=index, date_format="%Y-%m-%d")
        else:
            engine = get_parquet_engine()
            frame.to_parquet(
                temporary,
                index=index,
                engine=engine,
                compression=parquet_compression,
            )
        temporary.replace(destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise

    return destination


def read_df(
    path: str | Path,
    *,
    parse_dates: Sequence[str] | None = None,
    dtype: Mapping[str, Any] | None = None,
) -> pd.DataFrame:
    """Read a CSV or Parquet DataFrame, routing by suffix."""

    source = Path(path).expanduser()
    storage_format = detect_format(source)
    if not source.exists():
        raise FileNotFoundError(f"Data file does not exist: {source}")
    if not source.is_file():
        raise ValueError(f"Data path is not a regular file: {source}")

    if storage_format == "csv":
        return pd.read_csv(source, parse_dates=parse_dates, dtype=dtype)

    engine = get_parquet_engine()
    return pd.read_parquet(source, engine=engine)


def _matches_kind(series: pd.Series, expected_kind: str) -> bool:
    kind = expected_kind.lower()
    if kind == "datetime":
        return pd.api.types.is_datetime64_any_dtype(series)
    if kind == "numeric":
        return pd.api.types.is_numeric_dtype(series)
    if kind == "integer":
        return pd.api.types.is_integer_dtype(series)
    if kind == "float":
        return pd.api.types.is_float_dtype(series)
    if kind in {"string", "text"}:
        return pd.api.types.is_string_dtype(series)
    raise ValueError(
        f"Unsupported expected dtype kind {expected_kind!r}; "
        "use datetime, numeric, integer, float, or string"
    )


def validate_roundtrip(
    original: pd.DataFrame,
    reloaded: pd.DataFrame,
    critical_types: Mapping[str, str],
) -> dict[str, Any]:
    """Compare shape, columns, null counts, values, and critical dtype kinds."""

    missing_critical = [
        column for column in critical_types if column not in reloaded.columns
    ]
    dtype_checks = {
        column: {
            "expected_kind": expected_kind,
            "actual_dtype": str(reloaded[column].dtype),
            "passed": _matches_kind(reloaded[column], expected_kind),
        }
        for column, expected_kind in critical_types.items()
        if column in reloaded.columns
    }

    try:
        pd.testing.assert_frame_equal(
            original.reset_index(drop=True),
            reloaded.reset_index(drop=True),
            check_dtype=False,
            check_exact=False,
            rtol=1e-12,
            atol=1e-12,
        )
        values_equal = True
    except AssertionError:
        values_equal = False

    checks = {
        "shape_equal": original.shape == reloaded.shape,
        "column_order_equal": list(original.columns) == list(reloaded.columns),
        "null_counts_equal": original.isna().sum().equals(reloaded.isna().sum()),
        "values_equal": values_equal,
        "critical_columns_present": not missing_critical,
        "critical_dtypes_valid": bool(dtype_checks)
        and all(result["passed"] for result in dtype_checks.values()),
    }
    return {
        "original_shape": list(original.shape),
        "reloaded_shape": list(reloaded.shape),
        "checks": checks,
        "missing_critical_columns": missing_critical,
        "dtype_checks": dtype_checks,
        "passed": all(checks.values()),
    }
