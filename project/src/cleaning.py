"""Deterministic, auditable preprocessing for SPY daily OHLCV data."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

import pandas as pd


SPY_COLUMNS = ["date", "open", "high", "low", "close", "volume"]
PRICE_COLUMNS = ["open", "high", "low", "close"]


def clean_spy_ohlcv(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Return a canonically typed, sorted SPY OHLCV copy and its cleaning report.

    This policy intentionally fails on missing or invalid observations. It does
    not impute prices, remove outliers, or scale fields because those actions
    require later, separately documented financial and modeling decisions.
    """

    missing_columns = [column for column in SPY_COLUMNS if column not in frame.columns]
    if missing_columns:
        raise ValueError(f"SPY preprocessing input is missing columns: {missing_columns}")

    result = frame.loc[:, SPY_COLUMNS].copy(deep=True)
    input_dtypes = {column: str(dtype) for column, dtype in result.dtypes.items()}
    result["date"] = pd.to_datetime(result["date"], errors="raise")
    for column in [*PRICE_COLUMNS, "volume"]:
        result[column] = pd.to_numeric(result[column], errors="raise")

    missing_before = result.isna().sum().astype(int).to_dict()
    if any(missing_before.values()):
        raise ValueError(
            "SPY preprocessing does not impute missing OHLCV values: "
            f"{missing_before}"
        )
    if result["date"].duplicated().any():
        raise ValueError("SPY preprocessing input contains duplicate dates")
    if (result[PRICE_COLUMNS] <= 0).any().any():
        raise ValueError("SPY preprocessing input contains nonpositive prices")
    if (result["volume"] < 0).any():
        raise ValueError("SPY preprocessing input contains negative volume")

    invalid_ohlc = (
        (result["high"] < result["low"])
        | (result["high"] < result["open"])
        | (result["high"] < result["close"])
        | (result["low"] > result["open"])
        | (result["low"] > result["close"])
    )
    if invalid_ohlc.any():
        raise ValueError(f"SPY preprocessing input has {int(invalid_ohlc.sum())} invalid OHLC rows")

    was_monotonic = result["date"].is_monotonic_increasing
    result = result.sort_values("date", kind="stable").reset_index(drop=True)
    report = {
        "input_shape": list(frame.shape),
        "output_shape": list(result.shape),
        "input_dtypes": input_dtypes,
        "output_dtypes": {column: str(dtype) for column, dtype in result.dtypes.items()},
        "missing_before": missing_before,
        "missing_after": result.isna().sum().astype(int).to_dict(),
        "rows_dropped": 0,
        "sort_was_required": not was_monotonic,
        "date_min": result["date"].min().date().isoformat(),
        "date_max": result["date"].max().date().isoformat(),
        "policies": {
            "missing_values": "fail rather than impute",
            "invalid_rows": "fail rather than silently drop",
            "outliers": "not treated in Stage06; defer to Stage07",
            "scaling": "not applied; fit any future scaler on training data only",
        },
        "passed": True,
    }
    return result, report


def write_cleaning_report(report: dict[str, Any], path: str | Path) -> Path:
    """Atomically write a deterministic preprocessing report as JSON."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.temporary")
    try:
        temporary.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return destination
