"""Reusable exploratory-data-analysis summaries for Stage 08."""

from __future__ import annotations

from typing import Any

import pandas as pd


def _column_role(series: pd.Series) -> str:
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    if pd.api.types.is_bool_dtype(series):
        return "categorical"
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    return "categorical"


def _dominant_fraction(series: pd.Series) -> float:
    if series.empty:
        return 0.0
    counts = series.value_counts(dropna=False)
    return float(counts.iloc[0] / len(series)) if not counts.empty else 0.0


def eda_summary(
    frame: pd.DataFrame,
    *,
    high_missing_threshold: float = 0.20,
    near_zero_variance_threshold: float = 0.99,
    category_dominance_threshold: float = 0.95,
) -> dict[str, pd.DataFrame]:
    """Return reusable overview, profile, and attention tables for a DataFrame.

    Datetime columns receive temporal coverage checks instead of categorical
    value counts. Categorical output contains counts and proportions for every
    nonnumeric, nondatetime column. Attention flags identify any missingness,
    high missingness, near-zero variance, or a dominant category.
    """

    if not isinstance(frame, pd.DataFrame):
        raise TypeError("frame must be a pandas DataFrame")
    if frame.empty:
        raise ValueError("frame must contain at least one row")
    thresholds = {
        "high_missing_threshold": high_missing_threshold,
        "near_zero_variance_threshold": near_zero_variance_threshold,
        "category_dominance_threshold": category_dominance_threshold,
    }
    if any(not 0 <= value <= 1 for value in thresholds.values()):
        raise ValueError(f"Thresholds must be between 0 and 1: {thresholds}")

    overview = pd.DataFrame(
        [
            {
                "rows": len(frame),
                "columns": len(frame.columns),
                "missing_cells": int(frame.isna().sum().sum()),
                "duplicate_rows": int(frame.duplicated().sum()),
                "memory_bytes": int(frame.memory_usage(deep=True).sum()),
            }
        ]
    )

    column_records: list[dict[str, Any]] = []
    for column in frame.columns:
        series = frame[column]
        role = _column_role(series)
        missing_count = int(series.isna().sum())
        missing_fraction = float(missing_count / len(series))
        dominant_fraction = _dominant_fraction(series)
        unique_count = int(series.nunique(dropna=True))
        near_zero_variance = role != "datetime" and (
            unique_count <= 1 or dominant_fraction >= near_zero_variance_threshold
        )
        dominant_category = (
            role == "categorical" and dominant_fraction >= category_dominance_threshold
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

        column_records.append(
            {
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
            }
        )
    column_profile = pd.DataFrame(column_records)

    numeric_columns = column_profile.loc[
        column_profile["role"] == "numeric", "column"
    ].tolist()
    if numeric_columns:
        numeric_summary = frame[numeric_columns].describe().T
        numeric_summary["missing_count"] = frame[numeric_columns].isna().sum()
        numeric_summary["missing_fraction"] = frame[numeric_columns].isna().mean()
        numeric_summary["skew"] = frame[numeric_columns].skew()
        numeric_summary["kurtosis"] = frame[numeric_columns].kurt()
        numeric_summary["unique_count"] = frame[numeric_columns].nunique()
        numeric_summary = numeric_summary.rename_axis("column").reset_index()
    else:
        numeric_summary = pd.DataFrame(
            columns=[
                "column",
                "count",
                "mean",
                "std",
                "min",
                "25%",
                "50%",
                "75%",
                "max",
                "missing_count",
                "missing_fraction",
                "skew",
                "kurtosis",
                "unique_count",
            ]
        )

    categorical_records: list[dict[str, Any]] = []
    categorical_columns = column_profile.loc[
        column_profile["role"] == "categorical", "column"
    ].tolist()
    for column in categorical_columns:
        values = frame[column].astype("string").fillna("<MISSING>")
        counts = values.value_counts(dropna=False)
        for value, count in counts.items():
            categorical_records.append(
                {
                    "column": column,
                    "value": str(value),
                    "count": int(count),
                    "proportion": float(count / len(frame)),
                }
            )
    categorical_summary = pd.DataFrame(
        categorical_records,
        columns=["column", "value", "count", "proportion"],
    )

    datetime_records: list[dict[str, Any]] = []
    datetime_columns = column_profile.loc[
        column_profile["role"] == "datetime", "column"
    ].tolist()
    for column in datetime_columns:
        observed = frame[column].dropna()
        datetime_records.append(
            {
                "column": column,
                "minimum": observed.min() if not observed.empty else pd.NaT,
                "maximum": observed.max() if not observed.empty else pd.NaT,
                "unique_count": int(observed.nunique()),
                "duplicate_count": int(observed.duplicated().sum()),
                "monotonic_increasing": bool(observed.is_monotonic_increasing),
            }
        )
    datetime_summary = pd.DataFrame(
        datetime_records,
        columns=[
            "column",
            "minimum",
            "maximum",
            "unique_count",
            "duplicate_count",
            "monotonic_increasing",
        ],
    )

    attention = column_profile.loc[
        column_profile["attention"].ne("none"),
        [
            "column",
            "role",
            "missing_count",
            "missing_fraction",
            "dominant_fraction",
            "attention",
        ],
    ].reset_index(drop=True)

    return {
        "overview": overview,
        "column_profile": column_profile,
        "numeric_summary": numeric_summary,
        "categorical_summary": categorical_summary,
        "datetime_summary": datetime_summary,
        "attention": attention,
    }
