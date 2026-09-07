"""Reusable exploratory-data-analysis helpers for SPY market data."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


SPY_OHLCV_COLUMNS = ["date", "open", "high", "low", "close", "volume"]


def _column_role(series: pd.Series) -> str:
    """Classify a Series for concise EDA profiling."""

    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    if pd.api.types.is_bool_dtype(series):
        return "categorical"
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    return "categorical"


def _dominant_fraction(series: pd.Series) -> float:
    """Return the largest observed category proportion, including missingness."""

    if series.empty:
        return 0.0
    counts = series.value_counts(dropna=False)
    return float(counts.iloc[0] / len(series)) if not counts.empty else 0.0


def prepare_spy_eda_frame(frame: pd.DataFrame, *, volatility_window: int = 21) -> pd.DataFrame:
    """Return a sorted EDA-only SPY frame with transparent derived columns.

    Derived fields describe the historical snapshot only. They are not finalized
    Stage09 features and require time-safe lagging before future prediction.
    """

    if volatility_window < 2:
        raise ValueError("volatility_window must be at least 2")
    missing_columns = [column for column in SPY_OHLCV_COLUMNS if column not in frame.columns]
    if missing_columns:
        raise ValueError(f"SPY EDA input is missing columns: {missing_columns}")

    result = frame.copy(deep=True)
    result["date"] = pd.to_datetime(result["date"], errors="raise")
    for column in SPY_OHLCV_COLUMNS[1:]:
        result[column] = pd.to_numeric(result[column], errors="raise")
    if result[SPY_OHLCV_COLUMNS].isna().any().any():
        raise ValueError("SPY EDA base OHLCV values must be present")
    if result["date"].duplicated().any() or (result["open"] <= 0).any():
        raise ValueError("SPY EDA requires unique dates and positive open prices")

    result = result.sort_values("date", kind="stable").reset_index(drop=True)
    result["daily_return"] = result["close"].pct_change(fill_method=None)
    result["abs_return"] = result["daily_return"].abs()
    result["intraday_range"] = (result["high"] - result["low"]) / result["open"]
    result["close_to_open_return"] = result["close"] / result["open"] - 1
    result["log_volume"] = np.log1p(result["volume"])
    result["rolling_volatility_21"] = (
        result["daily_return"].rolling(volatility_window).std(ddof=1) * np.sqrt(252)
    )
    direction = pd.Series(
        np.select(
            [result["daily_return"].gt(0), result["daily_return"].lt(0)],
            ["Up", "Down"],
            default="Flat",
        ),
        index=result.index,
    )
    direction.loc[result["daily_return"].isna()] = "Missing"
    result["return_direction"] = pd.Categorical(
        direction, categories=["Down", "Flat", "Missing", "Up"]
    )
    result["weekday_name"] = pd.Categorical(result["date"].dt.day_name())
    return result


def eda_summary(
    frame: pd.DataFrame,
    *,
    high_missing_threshold: float = 0.20,
    near_zero_variance_threshold: float = 0.99,
    category_dominance_threshold: float = 0.95,
) -> dict[str, pd.DataFrame]:
    """Return reusable overview, profile, summary, and attention tables.

    Datetime columns receive coverage checks; categorical columns receive value
    counts. Attention flags identify missingness, near-zero variance, and a
    category that dominates its field before feature engineering begins.
    """

    if not isinstance(frame, pd.DataFrame):
        raise TypeError("frame must be a pandas DataFrame")
    if frame.empty:
        raise ValueError("frame must contain at least one row")
    thresholds = [
        high_missing_threshold,
        near_zero_variance_threshold,
        category_dominance_threshold,
    ]
    if any(not 0 <= value <= 1 for value in thresholds):
        raise ValueError("EDA thresholds must be between 0 and 1")

    overview = pd.DataFrame(
        [{
            "rows": len(frame),
            "columns": len(frame.columns),
            "missing_cells": int(frame.isna().sum().sum()),
            "duplicate_rows": int(frame.duplicated().sum()),
            "memory_bytes": int(frame.memory_usage(deep=True).sum()),
        }]
    )

    records: list[dict[str, Any]] = []
    for column in frame.columns:
        series = frame[column]
        role = _column_role(series)
        missing_count = int(series.isna().sum())
        missing_fraction = float(missing_count / len(series))
        unique_count = int(series.nunique(dropna=True))
        dominant_fraction = _dominant_fraction(series)
        near_zero_variance = role != "datetime" and (
            unique_count <= 1 or dominant_fraction >= near_zero_variance_threshold
        )
        dominant_category = role == "categorical" and (
            dominant_fraction >= category_dominance_threshold
        )
        attention: list[str] = []
        if missing_count:
            attention.append("has_missing")
        if missing_fraction >= high_missing_threshold:
            attention.append("high_missingness")
        if near_zero_variance:
            attention.append("near_zero_variance")
        if dominant_category:
            attention.append("dominant_category")
        records.append({
            "column": column,
            "role": role,
            "dtype": str(series.dtype),
            "non_null": int(series.notna().sum()),
            "missing_count": missing_count,
            "missing_fraction": missing_fraction,
            "unique_count": unique_count,
            "dominant_fraction": dominant_fraction,
            "near_zero_variance": near_zero_variance,
            "dominant_category": dominant_category,
            "attention": ";".join(attention) if attention else "none",
        })
    column_profile = pd.DataFrame(records)

    numeric_columns = column_profile.loc[column_profile["role"].eq("numeric"), "column"].tolist()
    if numeric_columns:
        numeric_summary = frame[numeric_columns].describe().T
        numeric_summary["missing_count"] = frame[numeric_columns].isna().sum()
        numeric_summary["missing_fraction"] = frame[numeric_columns].isna().mean()
        numeric_summary["skew"] = frame[numeric_columns].skew()
        numeric_summary["kurtosis"] = frame[numeric_columns].kurt()
        numeric_summary["unique_count"] = frame[numeric_columns].nunique()
        numeric_summary = numeric_summary.rename_axis("column").reset_index()
    else:
        numeric_summary = pd.DataFrame(columns=["column"])

    categorical_records: list[dict[str, Any]] = []
    categorical_columns = column_profile.loc[
        column_profile["role"].eq("categorical"), "column"
    ].tolist()
    for column in categorical_columns:
        values = frame[column].astype("string").fillna("<MISSING>")
        for value, count in values.value_counts(dropna=False).items():
            categorical_records.append({
                "column": column,
                "value": str(value),
                "count": int(count),
                "proportion": float(count / len(frame)),
            })
    categorical_summary = pd.DataFrame(
        categorical_records, columns=["column", "value", "count", "proportion"]
    )

    datetime_records: list[dict[str, Any]] = []
    datetime_columns = column_profile.loc[column_profile["role"].eq("datetime"), "column"].tolist()
    for column in datetime_columns:
        observed = frame[column].dropna()
        datetime_records.append({
            "column": column,
            "minimum": observed.min() if not observed.empty else pd.NaT,
            "maximum": observed.max() if not observed.empty else pd.NaT,
            "unique_count": int(observed.nunique()),
            "duplicate_count": int(observed.duplicated().sum()),
            "monotonic_increasing": bool(observed.is_monotonic_increasing),
        })
    datetime_summary = pd.DataFrame(datetime_records)

    attention = column_profile.loc[
        column_profile["attention"].ne("none"),
        ["column", "role", "missing_count", "missing_fraction", "dominant_fraction", "attention"],
    ].reset_index(drop=True)
    return {
        "overview": overview,
        "column_profile": column_profile,
        "numeric_summary": numeric_summary,
        "categorical_summary": categorical_summary,
        "datetime_summary": datetime_summary,
        "attention": attention,
    }
