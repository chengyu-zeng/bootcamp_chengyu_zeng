"""Acquire, validate, and document immutable-style SPY raw snapshots."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests


NASDAQ_HISTORY_URL = "https://api.nasdaq.com/api/quote/{symbol}/historical"
USER_AGENT = "NYU-AFE-Bootcamp-Project/1.0 (educational data acquisition)"


def timestamp_utc(now: datetime | None = None) -> str:
    """Return a UTC timestamp suitable for a reproducible raw filename."""

    current = now or datetime.now(UTC)
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    return current.astimezone(UTC).strftime("%Y%m%d-%H%M%S")


def fetch_nasdaq_history(
    symbol: str,
    start_date: str,
    end_date: str,
    *,
    timeout: int = 45,
    session: requests.Session | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Fetch and type daily unadjusted OHLCV data from Nasdaq's public endpoint."""

    normalized_symbol = symbol.strip().upper()
    if not normalized_symbol:
        raise ValueError("symbol must not be empty")

    url = NASDAQ_HISTORY_URL.format(symbol=normalized_symbol)
    params = {
        "assetclass": "etf",
        "fromdate": start_date,
        "todate": end_date,
        "limit": "5000",
    }
    client = session or requests
    response = client.get(
        url,
        params=params,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json, text/plain, */*",
            "Referer": f"https://www.nasdaq.com/market-activity/etf/{normalized_symbol.lower()}/historical",
        },
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()

    api_status = payload.get("status") or {}
    if api_status.get("rCode") != 200:
        raise RuntimeError(f"Nasdaq API rejected the request: {api_status}")

    data = payload.get("data") or {}
    rows = (data.get("tradesTable") or {}).get("rows") or []
    if not rows:
        raise ValueError("Nasdaq API returned no historical rows")

    required = ["date", "open", "high", "low", "close", "volume"]
    frame = pd.DataFrame(rows).rename(columns=str.lower)
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"Nasdaq response is missing columns: {missing}")

    frame = frame[required].copy()
    frame["date"] = pd.to_datetime(frame["date"], format="%m/%d/%Y", errors="raise")
    for column in ["open", "high", "low", "close", "volume"]:
        values = frame[column].astype("string").str.replace(r"[$,]", "", regex=True)
        frame[column] = pd.to_numeric(values, errors="coerce")

    incomplete_mask = frame[required].isna().any(axis=1)
    incomplete_rows = frame.loc[incomplete_mask, "date"].dt.date.astype(str).tolist()
    if incomplete_mask.mean() > 0.01:
        raise ValueError("More than 1% of source rows have incomplete or unparseable OHLCV values")
    frame = frame.loc[~incomplete_mask].sort_values("date", kind="stable").reset_index(drop=True)
    if frame.empty:
        raise ValueError("No complete Nasdaq rows remain after parsing")

    metadata = {
        "source": "Nasdaq public historical endpoint",
        "source_url": url,
        "request_params": params,
        "price_convention": "unadjusted OHLCV as supplied by the endpoint",
        "reported_total_records": int(data.get("totalRecords", len(frame))),
        "dropped_incomplete_rows": int(incomplete_mask.sum()),
        "dropped_incomplete_dates": incomplete_rows,
        "retrieved_at_utc": datetime.now(UTC).isoformat(),
    }
    return frame, metadata


def validate_spy_history(frame: pd.DataFrame) -> dict[str, Any]:
    """Fail early when a typed SPY daily OHLCV frame violates basic invariants."""

    required = ["date", "open", "high", "low", "close", "volume"]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"SPY data is missing required columns: {missing}")
    if frame.empty:
        raise ValueError("SPY data must contain at least one row")
    if not pd.api.types.is_datetime64_any_dtype(frame["date"]):
        raise TypeError("date must use a pandas datetime dtype")

    numeric = ["open", "high", "low", "close", "volume"]
    non_numeric = [column for column in numeric if not pd.api.types.is_numeric_dtype(frame[column])]
    if non_numeric:
        raise TypeError(f"Expected numeric columns: {non_numeric}")

    na_by_column = frame[required].isna().sum().astype(int).to_dict()
    problems = {
        "na_values": sum(na_by_column.values()),
        "duplicate_dates": int(frame["date"].duplicated().sum()),
        "non_monotonic_dates": not frame["date"].is_monotonic_increasing,
        "nonpositive_prices": int((frame[["open", "high", "low", "close"]] <= 0).sum().sum()),
        "negative_volume_rows": int((frame["volume"] < 0).sum()),
        "invalid_ohlc_rows": int(
            (
                (frame["high"] < frame["low"])
                | (frame["high"] < frame["open"])
                | (frame["high"] < frame["close"])
                | (frame["low"] > frame["open"])
                | (frame["low"] > frame["close"])
            ).sum()
        ),
    }
    if any(problems.values()):
        raise ValueError(f"SPY validation failed: {problems}")

    return {
        "shape": list(frame.shape),
        "required_columns_present": True,
        "dtypes": {column: str(dtype) for column, dtype in frame.dtypes.items()},
        "na_by_column": na_by_column,
        "date_min": frame["date"].min().date().isoformat(),
        "date_max": frame["date"].max().date().isoformat(),
        "passed": True,
    }


def write_raw_csv(frame: pd.DataFrame, raw_dir: str | Path, stem: str, *, timestamp: str) -> Path:
    """Write one timestamped raw CSV without overwriting an existing snapshot."""

    destination = Path(raw_dir)
    destination.mkdir(parents=True, exist_ok=True)
    safe_stem = re.sub(r"[^A-Za-z0-9_-]+", "_", stem).strip("_")
    path = destination / f"{safe_stem}_{timestamp}.csv"
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite raw snapshot: {path}")
    frame.to_csv(path, index=False, date_format="%Y-%m-%d")
    return path


def write_manifest(record: dict[str, Any], output_path: str | Path) -> Path:
    """Write provenance, validation, and checksum metadata for a raw snapshot."""

    source_path = Path(record["path"])
    digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
    manifest = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "artifacts": [
            {
                **record,
                "path": source_path.name,
                "sha256": digest,
                "size_bytes": source_path.stat().st_size,
            }
        ],
    }
    target = Path(output_path)
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite raw manifest: {target}")
    target.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target
