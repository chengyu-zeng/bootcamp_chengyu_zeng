"""Reusable tabular-data helpers for the SPY risk-alert project."""

from __future__ import annotations

import re
from collections.abc import Iterable

import pandas as pd
from pandas.api.types import is_numeric_dtype


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with lowercase, underscore-separated column names.

    The helper makes source schemas easier to reference consistently while
    refusing names that become blank or duplicated after normalization.
    """

    cleaned = [re.sub(r"[^a-z0-9]+", "_", str(name).lower()).strip("_") for name in df.columns]
    if not all(cleaned):
        raise ValueError("Column names cannot be empty after normalization.")
    if len(cleaned) != len(set(cleaned)):
        raise ValueError("Column names must remain unique after normalization.")

    result = df.copy()
    result.columns = cleaned
    return result


def require_columns(df: pd.DataFrame, columns: Iterable[str]) -> None:
    """Raise a clear error when one or more required columns are absent."""

    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def get_summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Return tidy descriptive statistics for numeric columns in ``df``."""

    numeric = df.select_dtypes(include="number")
    if numeric.empty:
        raise ValueError("The dataframe has no numeric columns to summarize.")
    return numeric.describe().T.rename_axis("feature").reset_index()


def get_group_summary(
    df: pd.DataFrame,
    *,
    group_col: str,
    value_col: str,
) -> pd.DataFrame:
    """Return count, mean, and standard deviation for a numeric value by group."""

    require_columns(df, [group_col, value_col])
    if not is_numeric_dtype(df[value_col]):
        raise TypeError(f"{value_col!r} must be numeric.")

    return (
        df.groupby(group_col, observed=True)[value_col]
        .agg(["count", "mean", "std"])
        .rename_axis(group_col)
        .reset_index()
        .sort_values(group_col, kind="stable")
        .reset_index(drop=True)
    )
