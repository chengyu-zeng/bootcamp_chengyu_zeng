"""Reusable outlier detection and treatment functions for Stage 07."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd


def _validated_numeric_series(series: pd.Series) -> pd.Series:
    if not isinstance(series, pd.Series):
        raise TypeError("series must be a pandas Series")
    if series.empty:
        raise ValueError("series must contain at least one observation")
    if not pd.api.types.is_numeric_dtype(series):
        raise TypeError("series must have a numeric dtype")

    observed = series.dropna()
    if observed.empty:
        raise ValueError("series must contain at least one non-missing observation")
    if not np.isfinite(observed.to_numpy(dtype="float64")).all():
        raise ValueError("series must not contain infinite values")
    return observed


def _validated_positive(value: float, name: str) -> float:
    numeric = float(value)
    if not math.isfinite(numeric) or numeric <= 0:
        raise ValueError(f"{name} must be a finite positive number")
    return numeric


def detect_outliers_iqr(series: pd.Series, k: float = 1.5) -> pd.Series:
    """Return an aligned boolean mask for observations outside IQR fences.

    Fences are ``Q1 - k * IQR`` and ``Q3 + k * IQR``. Missing observations
    are not flagged. This rule is distribution-free but can flag legitimate
    tail observations and can be sensitive when the sample is small.
    """

    observed = _validated_numeric_series(series)
    multiplier = _validated_positive(k, "k")
    first_quartile = observed.quantile(0.25)
    third_quartile = observed.quantile(0.75)
    interquartile_range = third_quartile - first_quartile
    lower_bound = first_quartile - multiplier * interquartile_range
    upper_bound = third_quartile + multiplier * interquartile_range
    return ((series < lower_bound) | (series > upper_bound)).fillna(False).astype(bool)


def detect_outliers_zscore(
    series: pd.Series,
    threshold: float = 3.0,
) -> pd.Series:
    """Return an aligned boolean mask where the population absolute z-score is high.

    The mean and population standard deviation (``ddof=0``) are estimated from
    non-missing observations. Missing observations and all observations in a
    constant series are not flagged. The rule assumes a roughly symmetric,
    light-tailed distribution and can be distorted by the extremes it seeks.
    """

    observed = _validated_numeric_series(series)
    cutoff = _validated_positive(threshold, "threshold")
    standard_deviation = observed.std(ddof=0)
    if standard_deviation == 0:
        return pd.Series(False, index=series.index, dtype=bool)

    z_scores = (series - observed.mean()) / standard_deviation
    return z_scores.abs().gt(cutoff).fillna(False).astype(bool)


def winsorize_series(
    series: pd.Series,
    lower: float = 0.05,
    upper: float = 0.95,
) -> pd.Series:
    """Clip observations to validated lower and upper empirical quantiles.

    Missing values remain missing. Winsorizing retains every row but replaces
    tail magnitudes, so it should be treated as an assumption rather than a
    neutral cleaning step.
    """

    observed = _validated_numeric_series(series)
    lower_quantile = float(lower)
    upper_quantile = float(upper)
    if not (
        math.isfinite(lower_quantile)
        and math.isfinite(upper_quantile)
        and 0 <= lower_quantile < upper_quantile <= 1
    ):
        raise ValueError("Require 0 <= lower < upper <= 1")

    lower_bound = observed.quantile(lower_quantile)
    upper_bound = observed.quantile(upper_quantile)
    return series.clip(lower=lower_bound, upper=upper_bound)
