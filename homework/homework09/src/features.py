"""Leakage-aware feature construction for Stage09 SPY homework."""

from __future__ import annotations

import numpy as np
import pandas as pd


BASE_COLUMNS = ["date", "open", "high", "low", "close", "volume"]


def build_spy_features(frame: pd.DataFrame, *, volatility_window: int = 5) -> pd.DataFrame:
    """Return a dated SPY feature table and continuous next-day outcome.

    Features at date t use data available after t's close. `next_day_abs_return`
    is an outcome created with a negative shift and is never a feature. The final
    outcome is structurally missing because no next trading day is retained.
    """

    if volatility_window < 2:
        raise ValueError("volatility_window must be at least 2")
    missing = [column for column in BASE_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing SPY columns: {missing}")
    result = frame.loc[:, BASE_COLUMNS].copy(deep=True)
    result["date"] = pd.to_datetime(result["date"], errors="raise")
    for column in BASE_COLUMNS[1:]:
        result[column] = pd.to_numeric(result[column], errors="raise")
    if result[BASE_COLUMNS].isna().any().any() or result["date"].duplicated().any():
        raise ValueError("SPY features require complete OHLCV values and unique dates")
    if (result[["open", "high", "low", "close"]] <= 0).any().any() or (result["volume"] < 0).any():
        raise ValueError("SPY features require positive prices and nonnegative volume")

    result = result.sort_values("date", kind="stable").reset_index(drop=True)
    result["return_t"] = result["close"].pct_change(fill_method=None)
    result["abs_return_t"] = result["return_t"].abs()
    result["intraday_range_t"] = (result["high"] - result["low"]) / result["open"]
    log_volume = np.log1p(result["volume"])
    result["log_volume_change_t"] = log_volume.diff()
    result["rolling_volatility_5_t"] = (
        result["return_t"].rolling(volatility_window).std(ddof=1) * np.sqrt(252)
    )
    result["stress_interaction_t"] = result["abs_return_t"] * result["intraday_range_t"]
    weekday = result["date"].dt.day_name()
    weekday_dummies = pd.get_dummies(weekday, prefix="weekday", dtype="int8")
    result = pd.concat([result, weekday_dummies], axis=1)
    result["next_day_abs_return"] = result["return_t"].shift(-1).abs()
    return result


def feature_target_correlation(
    frame: pd.DataFrame,
    *,
    target_column: str = "next_day_abs_return",
) -> pd.DataFrame:
    """Return pairwise Pearson correlations for numeric candidate features.

    This is an exploratory diagnostic, not feature selection proof or a causal
    claim. Rows with structural warm-up/terminal missingness are omitted only
    for the corresponding pairwise calculation.
    """

    if target_column not in frame.columns:
        raise ValueError(f"Target column is missing: {target_column}")
    target = pd.to_numeric(frame[target_column], errors="raise")
    excluded = {"open", "high", "low", "close", "volume", target_column}
    candidates = [
        column for column in frame.columns
        if column not in excluded and pd.api.types.is_numeric_dtype(frame[column])
    ]
    records = []
    for column in candidates:
        values = pd.to_numeric(frame[column], errors="raise")
        valid = values.notna() & target.notna()
        records.append({
            "feature": column,
            "observations": int(valid.sum()),
            "pearson_correlation": float(values.loc[valid].corr(target.loc[valid])),
        })
    return pd.DataFrame(records).sort_values("pearson_correlation", key=lambda x: x.abs(), ascending=False).reset_index(drop=True)
