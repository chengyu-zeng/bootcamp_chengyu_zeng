"""Reusable, descriptive outlier analysis for SPY daily returns."""

from __future__ import annotations

import json
import math
import uuid
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def _observed_numeric(series: pd.Series) -> pd.Series:
    """Validate a numeric Series and return its finite, non-missing values."""

    if not isinstance(series, pd.Series):
        raise TypeError("series must be a pandas Series")
    if series.empty:
        raise ValueError("series must contain at least one observation")

    numeric = pd.to_numeric(series, errors="raise")
    observed = numeric.dropna()
    if observed.empty:
        raise ValueError("series must contain at least one non-missing observation")
    if not np.isfinite(observed.to_numpy(dtype="float64")).all():
        raise ValueError("series must not contain infinite values")
    return observed


def _positive_finite(value: float, name: str) -> float:
    """Validate a finite positive numeric parameter."""

    numeric = float(value)
    if not math.isfinite(numeric) or numeric <= 0:
        raise ValueError(f"{name} must be a finite positive number")
    return numeric


def iqr_bounds(series: pd.Series, k: float = 1.5) -> tuple[float, float]:
    """Return Tukey IQR fences estimated from finite, non-missing observations."""

    observed = _observed_numeric(series)
    multiplier = _positive_finite(k, "k")
    first_quartile, third_quartile = observed.quantile([0.25, 0.75])
    interquartile_range = third_quartile - first_quartile
    return (
        float(first_quartile - multiplier * interquartile_range),
        float(third_quartile + multiplier * interquartile_range),
    )


def detect_outliers_iqr(series: pd.Series, k: float = 1.5) -> pd.Series:
    """Return an aligned boolean mask for values outside Tukey IQR fences.

    Missing observations remain unflagged. The method is robust to skew but may
    flag economically meaningful tail returns, so it is a review flag rather
    than a rule to remove dates.
    """

    lower_bound, upper_bound = iqr_bounds(series, k=k)
    numeric = pd.to_numeric(series, errors="raise")
    return ((numeric < lower_bound) | (numeric > upper_bound)).fillna(False).astype(bool)


def detect_outliers_zscore(series: pd.Series, threshold: float = 3.0) -> pd.Series:
    """Return an aligned mask for values above a population absolute z-score.

    Missing values and constant Series values remain unflagged. This diagnostic
    assumes a roughly symmetric, light-tailed distribution and can be unstable
    for financial returns with heavy tails.
    """

    observed = _observed_numeric(series)
    cutoff = _positive_finite(threshold, "threshold")
    standard_deviation = observed.std(ddof=0)
    if standard_deviation == 0:
        return pd.Series(False, index=series.index, dtype=bool)
    z_scores = (pd.to_numeric(series, errors="raise") - observed.mean()) / standard_deviation
    return z_scores.abs().gt(cutoff).fillna(False).astype(bool)


def winsorize_series(
    series: pd.Series,
    lower: float = 0.05,
    upper: float = 0.95,
) -> pd.Series:
    """Clip a Series to empirical quantile bounds while preserving missing values."""

    observed = _observed_numeric(series)
    lower_quantile = float(lower)
    upper_quantile = float(upper)
    if not (
        math.isfinite(lower_quantile)
        and math.isfinite(upper_quantile)
        and 0 <= lower_quantile < upper_quantile <= 1
    ):
        raise ValueError("Require 0 <= lower < upper <= 1")
    return pd.to_numeric(series, errors="raise").clip(
        lower=observed.quantile(lower_quantile),
        upper=observed.quantile(upper_quantile),
    )


def analyze_daily_return_outliers(
    frame: pd.DataFrame,
    *,
    date_column: str = "date",
    close_column: str = "close",
    iqr_k: float = 1.5,
    zscore_threshold: float = 3.0,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Add daily-return flags without removing or altering market dates.

    The first return is missing by construction because it has no prior close;
    it is retained and unflagged. Thresholds use the full retained snapshot for
    this Stage07 descriptive analysis only, not future model preprocessing.
    """

    required = [date_column, close_column]
    missing_columns = [column for column in required if column not in frame.columns]
    if missing_columns:
        raise ValueError(f"Input is missing required columns: {missing_columns}")

    result = frame.copy(deep=True)
    result[date_column] = pd.to_datetime(result[date_column], errors="raise")
    result[close_column] = pd.to_numeric(result[close_column], errors="raise")
    if result[date_column].isna().any() or result[close_column].isna().any():
        raise ValueError("Date and close values must be present for return analysis")
    if result[date_column].duplicated().any():
        raise ValueError("Return analysis input contains duplicate dates")
    if (result[close_column] <= 0).any():
        raise ValueError("Return analysis input contains nonpositive close values")

    sort_was_required = not result[date_column].is_monotonic_increasing
    result = result.sort_values(date_column, kind="stable").reset_index(drop=True)
    result["daily_return"] = result[close_column].pct_change(fill_method=None)
    result["return_outlier_iqr"] = detect_outliers_iqr(result["daily_return"], k=iqr_k)
    result["return_outlier_zscore"] = detect_outliers_zscore(
        result["daily_return"], threshold=zscore_threshold
    )

    lower_bound, upper_bound = iqr_bounds(result["daily_return"], k=iqr_k)
    report = {
        "input_shape": list(frame.shape),
        "output_shape": list(result.shape),
        "date_min": result[date_column].min().date().isoformat(),
        "date_max": result[date_column].max().date().isoformat(),
        "return_observations": int(result["daily_return"].notna().sum()),
        "first_return_missing_by_construction": int(result["daily_return"].isna().sum()),
        "sort_was_required": sort_was_required,
        "iqr": {
            "k": float(iqr_k),
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "flagged_count": int(result["return_outlier_iqr"].sum()),
        },
        "zscore": {
            "threshold": float(zscore_threshold),
            "flagged_count": int(result["return_outlier_zscore"].sum()),
        },
        "policy": {
            "default_action": "flag and retain all observations",
            "scope": "full-snapshot descriptive sensitivity analysis only",
            "future_modeling": "estimate thresholds on training data only",
        },
        "passed": True,
    }
    return result, report


def summarize_return_sensitivity(
    analyzed: pd.DataFrame,
    *,
    return_column: str = "daily_return",
    iqr_flag_column: str = "return_outlier_iqr",
    winsor_lower: float = 0.05,
    winsor_upper: float = 0.95,
) -> pd.DataFrame:
    """Compare retained, IQR-filtered, and winsorized return distributions.

    Filtering and winsorizing are counterfactual diagnostics, not replacements
    for the retained market-return series used by later project stages.
    """

    required = [return_column, iqr_flag_column]
    missing_columns = [column for column in required if column not in analyzed.columns]
    if missing_columns:
        raise ValueError(f"Analysis data are missing columns: {missing_columns}")

    returns = pd.to_numeric(analyzed[return_column], errors="raise")
    iqr_flags = analyzed[iqr_flag_column].astype(bool)
    variants = {
        "all": returns,
        "filtered_iqr": returns.loc[~iqr_flags],
        f"winsorized_{winsor_lower:g}_{winsor_upper:g}": winsorize_series(
            returns, lower=winsor_lower, upper=winsor_upper
        ),
    }
    return pd.DataFrame(
        [
            {
                "variant": name,
                "observations": int(values.notna().sum()),
                "mean": float(values.mean()),
                "median": float(values.median()),
                "std": float(values.std(ddof=1)),
                "minimum": float(values.min()),
                "maximum": float(values.max()),
            }
            for name, values in variants.items()
        ]
    )


def write_outlier_report(report: dict[str, Any], path: str | Path) -> Path:
    """Atomically write a deterministic Stage07 analysis report as JSON."""

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
