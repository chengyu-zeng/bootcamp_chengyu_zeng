"""Leakage-aware Stage09 feature construction for the SPY risk-alert project."""

from __future__ import annotations

import numpy as np
import pandas as pd


BASE_COLUMNS = ["date", "open", "high", "low", "close", "volume"]


def build_spy_features(frame: pd.DataFrame, *, volatility_window: int = 5) -> pd.DataFrame:
    """Build end-of-day feature candidates and a next-day continuous outcome.

    Every ``*_t`` feature uses only information known after the market close on
    date ``t``. ``next_day_abs_return`` is shifted backward solely as a later
    modeling outcome; it is never an input feature. The final row therefore has
    a structural missing outcome because the snapshot contains no next session.
    """

    if volatility_window < 2:
        raise ValueError("volatility_window must be at least 2")
    missing_columns = [column for column in BASE_COLUMNS if column not in frame.columns]
    if missing_columns:
        raise ValueError(f"SPY feature input is missing columns: {missing_columns}")

    result = frame.loc[:, BASE_COLUMNS].copy(deep=True)
    result["date"] = pd.to_datetime(result["date"], errors="raise")
    for column in BASE_COLUMNS[1:]:
        result[column] = pd.to_numeric(result[column], errors="raise")
    if result[BASE_COLUMNS].isna().any().any():
        raise ValueError("SPY features require complete base OHLCV values")
    if result["date"].duplicated().any():
        raise ValueError("SPY features require unique dates")
    if (result[["open", "high", "low", "close"]] <= 0).any().any():
        raise ValueError("SPY features require positive prices")
    if (result["volume"] < 0).any():
        raise ValueError("SPY features require nonnegative volume")

    result = result.sort_values("date", kind="stable").reset_index(drop=True)
    result["return_t"] = result["close"].pct_change(fill_method=None)
    result["abs_return_t"] = result["return_t"].abs()
    result["intraday_range_t"] = (result["high"] - result["low"]) / result["open"]
    result["log_volume_change_t"] = np.log1p(result["volume"]).diff()
    result["rolling_volatility_5_t"] = (
        result["return_t"].rolling(volatility_window).std(ddof=1) * np.sqrt(252)
    )
    result["stress_interaction_t"] = result["abs_return_t"] * result["intraday_range_t"]

    weekday_dummies = pd.get_dummies(
        result["date"].dt.day_name(), prefix="weekday", dtype="int8"
    )
    expected_weekdays = [f"weekday_{day}" for day in [
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"
    ]]
    weekday_dummies = weekday_dummies.reindex(columns=expected_weekdays, fill_value=0)
    result = pd.concat([result, weekday_dummies], axis=1)

    result["next_day_abs_return"] = result["return_t"].shift(-1).abs()
    return result


def feature_target_correlation(
    frame: pd.DataFrame,
    *,
    target_column: str = "next_day_abs_return",
) -> pd.DataFrame:
    """Calculate pairwise Pearson diagnostics for numeric feature candidates.

    The calculation is descriptive screening only: it is neither a causal claim
    nor a substitute for chronological validation or train-only feature choice.
    Structural warm-up and terminal values are omitted pairwise.
    """

    if target_column not in frame.columns:
        raise ValueError(f"Target column is missing: {target_column}")
    target = pd.to_numeric(frame[target_column], errors="raise")
    excluded = {"date", "open", "high", "low", "close", "volume", target_column}
    candidates = [
        column
        for column in frame.columns
        if column not in excluded and pd.api.types.is_numeric_dtype(frame[column])
    ]
    records: list[dict[str, float | int | str]] = []
    for column in candidates:
        values = pd.to_numeric(frame[column], errors="raise")
        valid = values.notna() & target.notna()
        records.append({
            "feature": column,
            "observations": int(valid.sum()),
            "pearson_correlation": float(values.loc[valid].corr(target.loc[valid])),
        })
    return pd.DataFrame(records).sort_values(
        "pearson_correlation", key=lambda series: series.abs(), ascending=False
    ).reset_index(drop=True)
