"""Reusable acquisition, validation, and raw-snapshot helpers for Stage 04."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from bs4 import BeautifulSoup

NASDAQ_HISTORY_URL = "https://api.nasdaq.com/api/quote/{symbol}/historical"
SP500_CONSTITUENTS_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
USER_AGENT = "NYU-AFE-Bootcamp-Homework/1.0 (educational data acquisition)"


def timestamp_utc(now: datetime | None = None) -> str:
    """Return the Stage 04 filename timestamp in UTC."""

    current = now or datetime.now(UTC)
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    return current.astimezone(UTC).strftime("%Y%m%d-%H%M")


def _request_headers(*, referer: str | None = None) -> dict[str, str]:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/html;q=0.9, */*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    if referer:
        headers["Referer"] = referer
    return headers


def fetch_nasdaq_history(
    symbol: str,
    start_date: str,
    end_date: str,
    *,
    timeout: int = 45,
    session: requests.Session | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Fetch daily OHLCV history from Nasdaq's public JSON endpoint."""

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
        headers=_request_headers(
            referer=(
                f"https://www.nasdaq.com/market-activity/etf/"
                f"{normalized_symbol.lower()}/historical"
            )
        ),
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

    frame = pd.DataFrame(rows).rename(columns=str.lower)
    required = ["date", "open", "high", "low", "close", "volume"]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"Nasdaq response is missing columns: {missing}")

    frame = frame[required].copy()
    frame["date"] = pd.to_datetime(frame["date"], format="%m/%d/%Y", errors="raise")
    for column in ["open", "high", "low", "close", "volume"]:
        cleaned = frame[column].astype("string").str.replace(r"[$,]", "", regex=True)
        frame[column] = pd.to_numeric(cleaned, errors="coerce")

    incomplete_mask = frame[required].isna().any(axis=1)
    incomplete_rows = frame.loc[incomplete_mask].copy()
    if incomplete_mask.mean() > 0.01:
        raise ValueError(
            "More than 1% of Nasdaq rows contain unparseable or missing OHLCV values"
        )
    frame = frame.loc[~incomplete_mask].copy()
    if frame.empty:
        raise ValueError("No complete Nasdaq rows remain after numeric parsing")

    frame = frame.sort_values("date", kind="stable").reset_index(drop=True)
    metadata = {
        "source": "Nasdaq",
        "source_url": url,
        "request_params": params,
        "reported_total_records": int(data.get("totalRecords", len(frame))),
        "dropped_incomplete_rows": int(incomplete_mask.sum()),
        "dropped_incomplete_dates": [
            value.date().isoformat() for value in incomplete_rows["date"]
        ],
        "retrieved_at_utc": datetime.now(UTC).isoformat(),
    }
    return frame, metadata


def validate_spy_history(frame: pd.DataFrame) -> dict[str, Any]:
    """Validate the SPY schema, types, completeness, and market invariants."""

    required = ["date", "open", "high", "low", "close", "volume"]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"SPY data is missing required columns: {missing}")
    if frame.empty:
        raise ValueError("SPY data must contain at least one row")

    numeric = ["open", "high", "low", "close", "volume"]
    if not pd.api.types.is_datetime64_any_dtype(frame["date"]):
        raise TypeError("date must be parsed as a pandas datetime dtype")
    non_numeric = [
        column for column in numeric if not pd.api.types.is_numeric_dtype(frame[column])
    ]
    if non_numeric:
        raise TypeError(f"Expected numeric columns: {non_numeric}")

    na_by_column = frame[required].isna().sum().astype(int).to_dict()
    duplicate_dates = int(frame["date"].duplicated().sum())
    nonpositive_prices = int((frame[["open", "high", "low", "close"]] <= 0).sum().sum())
    negative_volume = int((frame["volume"] < 0).sum())
    invalid_ranges = int(
        (
            (frame["high"] < frame["low"])
            | (frame["high"] < frame["open"])
            | (frame["high"] < frame["close"])
            | (frame["low"] > frame["open"])
            | (frame["low"] > frame["close"])
        ).sum()
    )

    problems = {
        "na_values": sum(na_by_column.values()),
        "duplicate_dates": duplicate_dates,
        "nonpositive_prices": nonpositive_prices,
        "negative_volume_rows": negative_volume,
        "invalid_ohlc_rows": invalid_ranges,
    }
    if any(problems.values()):
        raise ValueError(f"SPY validation failed: {problems}")

    return {
        "shape": list(frame.shape),
        "required_columns_present": True,
        "dtypes": {column: str(dtype) for column, dtype in frame.dtypes.items()},
        "na_by_column": na_by_column,
        "duplicate_dates": duplicate_dates,
        "date_min": frame["date"].min().date().isoformat(),
        "date_max": frame["date"].max().date().isoformat(),
        "invalid_ohlc_rows": invalid_ranges,
        "passed": True,
    }


def _snake_case(label: str) -> str:
    cleaned = re.sub(r"[^0-9A-Za-z]+", "_", label.strip()).strip("_")
    return cleaned.lower()


def scrape_sp500_constituents(
    *,
    timeout: int = 45,
    session: requests.Session | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Scrape the current S&P 500 constituents table from Wikipedia."""

    client = session or requests
    response = client.get(
        SP500_CONSTITUENTS_URL,
        headers=_request_headers(),
        timeout=timeout,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", id="constituents")
    if table is None:
        raise ValueError("Could not find table#constituents on the source page")

    rows = table.find_all("tr")
    header = [
        _snake_case(cell.get_text(" ", strip=True)) for cell in rows[0].find_all("th")
    ]
    records: list[list[str]] = []
    for row in rows[1:]:
        values = [cell.get_text(" ", strip=True) for cell in row.find_all("td")]
        if values:
            if len(values) != len(header):
                raise ValueError(
                    f"Unexpected constituents row width: {len(values)} != {len(header)}"
                )
            records.append(values)

    frame = pd.DataFrame(records, columns=header)
    if "cik" in frame.columns:
        frame["cik"] = pd.to_numeric(frame["cik"], errors="raise").astype("int64")
    if "date_added" in frame.columns:
        frame["date_added"] = pd.to_datetime(frame["date_added"], errors="coerce")

    metadata = {
        "source": "Wikipedia",
        "source_url": SP500_CONSTITUENTS_URL,
        "table_selector": "table#constituents",
        "retrieved_at_utc": datetime.now(UTC).isoformat(),
    }
    return frame, metadata


def validate_sp500_constituents(frame: pd.DataFrame) -> dict[str, Any]:
    """Validate text, numeric, uniqueness, and plausible row-count properties."""

    required = ["symbol", "security", "gics_sector", "gics_sub_industry", "cik"]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"Constituent data is missing required columns: {missing}")
    if len(frame) < 400:
        raise ValueError(
            f"Expected at least 400 constituent rows, received {len(frame)}"
        )
    if not pd.api.types.is_numeric_dtype(frame["cik"]):
        raise TypeError("cik must be converted to a numeric dtype")

    blank_text = {
        column: int(frame[column].astype("string").str.strip().eq("").sum())
        for column in ["symbol", "security", "gics_sector", "gics_sub_industry"]
    }
    duplicate_symbols = int(frame["symbol"].duplicated().sum())
    invalid_cik = int((frame["cik"] <= 0).sum())
    sector_count = int(frame["gics_sector"].nunique())
    if any(blank_text.values()) or duplicate_symbols or invalid_cik or sector_count < 8:
        raise ValueError(
            "Constituent validation failed: "
            f"blank_text={blank_text}, duplicate_symbols={duplicate_symbols}, "
            f"invalid_cik={invalid_cik}, sector_count={sector_count}"
        )

    return {
        "shape": list(frame.shape),
        "required_columns_present": True,
        "dtypes": {column: str(dtype) for column, dtype in frame.dtypes.items()},
        "na_by_column": frame.isna().sum().astype(int).to_dict(),
        "blank_text": blank_text,
        "duplicate_symbols": duplicate_symbols,
        "unique_sectors": sector_count,
        "numeric_cik": True,
        "passed": True,
    }


def write_raw_csv(
    frame: pd.DataFrame,
    raw_dir: str | Path,
    filename_stem: str,
    *,
    timestamp: str | None = None,
) -> Path:
    """Write an immutable-style timestamped raw CSV and return its path."""

    destination = Path(raw_dir)
    destination.mkdir(parents=True, exist_ok=True)
    safe_stem = re.sub(r"[^A-Za-z0-9_-]+", "_", filename_stem).strip("_")
    path = destination / f"{safe_stem}_{timestamp or timestamp_utc()}.csv"
    frame.to_csv(path, index=False, date_format="%Y-%m-%d")
    return path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(
    records: list[dict[str, Any]],
    output_path: str | Path,
) -> Path:
    """Write source, validation, and checksum metadata for raw snapshots."""

    normalized: list[dict[str, Any]] = []
    for record in records:
        path = Path(record["path"])
        normalized.append(
            {
                **record,
                "path": path.name,
                "sha256": _sha256(path),
                "size_bytes": path.stat().st_size,
            }
        )

    manifest = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "artifacts": normalized,
    }
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(manifest, indent=2, default=str) + "\n", encoding="utf-8"
    )
    return target
