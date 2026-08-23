"""Reusable pandas summary helpers for Stage 03."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd
from pandas.api.types import is_numeric_dtype


def require_columns(df: pd.DataFrame, columns: Iterable[str]) -> None:
    """Raise a clear error when required columns are absent."""

    required = list(columns)
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def get_summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Return tidy descriptive statistics for every numeric column."""

    numeric = df.select_dtypes(include="number")
    if numeric.empty:
        raise ValueError("The dataframe has no numeric columns to summarize.")

    return numeric.describe().T.rename_axis("feature").reset_index()


def get_category_summary(
    df: pd.DataFrame,
    *,
    category_col: str = "category",
    value_col: str = "value",
) -> pd.DataFrame:
    """Aggregate count and distribution statistics by category."""

    require_columns(df, [category_col, value_col])
    if not is_numeric_dtype(df[value_col]):
        raise TypeError(f"{value_col!r} must be numeric.")

    return (
        df.groupby(category_col, observed=True)[value_col]
        .agg(["count", "mean", "median", "min", "max"])
        .rename_axis(category_col)
        .reset_index()
        .sort_values(category_col, kind="stable")
        .reset_index(drop=True)
    )
