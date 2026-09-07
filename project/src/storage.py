"""Suffix-routed, environment-independent DataFrame storage helpers."""

from __future__ import annotations

import importlib.util
import uuid
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import pandas as pd


StorageFormat = Literal["csv", "parquet"]
PARQUET_SUFFIXES = {".parquet", ".parq", ".pq"}


def detect_format(path: str | Path) -> StorageFormat:
    """Return the supported storage format inferred from a file suffix."""

    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        return "csv"
    if suffix in PARQUET_SUFFIXES:
        return "parquet"
    raise ValueError(
        f"Unsupported file suffix {suffix or '<none>'!r}; use .csv, .parquet, .parq, or .pq"
    )


def get_parquet_engine() -> str:
    """Return an installed Parquet engine or raise an actionable error."""

    for engine in ("pyarrow", "fastparquet"):
        if importlib.util.find_spec(engine) is not None:
            return engine
    raise RuntimeError(
        "Parquet support is unavailable. Install `pyarrow` (recommended) or `fastparquet`."
    )


def write_df(
    frame: pd.DataFrame,
    path: str | Path,
    *,
    index: bool = False,
    parquet_compression: str = "snappy",
) -> Path:
    """Atomically write a DataFrame as CSV or Parquet according to its suffix."""

    if not isinstance(frame, pd.DataFrame):
        raise TypeError("frame must be a pandas DataFrame")

    destination = Path(path).expanduser()
    storage_format = detect_format(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.temporary")

    try:
        if storage_format == "csv":
            frame.to_csv(temporary, index=index, date_format="%Y-%m-%d")
        else:
            frame.to_parquet(
                temporary,
                index=index,
                engine=get_parquet_engine(),
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
    """Read CSV or Parquet while giving missing files and engines clear errors."""

    source = Path(path).expanduser()
    storage_format = detect_format(source)
    if not source.exists():
        raise FileNotFoundError(f"Data file does not exist: {source}")
    if not source.is_file():
        raise ValueError(f"Data path is not a regular file: {source}")
    if storage_format == "csv":
        return pd.read_csv(source, parse_dates=parse_dates, dtype=dtype)
    return pd.read_parquet(source, engine=get_parquet_engine())


def _matches_kind(series: pd.Series, expected_kind: str) -> bool:
    """Check a portable high-level dtype category rather than an exact dtype string."""

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
    raise ValueError("Expected dtype kind: datetime, numeric, integer, float, or string")


def validate_roundtrip(
    original: pd.DataFrame,
    reloaded: pd.DataFrame,
    critical_types: Mapping[str, str],
) -> dict[str, Any]:
    """Compare shape, columns, null counts, values, and critical dtype categories."""

    missing = [column for column in critical_types if column not in reloaded.columns]
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
        "critical_columns_present": not missing,
        "critical_dtypes_valid": bool(dtype_checks)
        and all(detail["passed"] for detail in dtype_checks.values()),
    }
    return {
        "original_shape": list(original.shape),
        "reloaded_shape": list(reloaded.shape),
        "checks": checks,
        "missing_critical_columns": missing,
        "dtype_checks": dtype_checks,
        "passed": all(checks.values()),
    }
