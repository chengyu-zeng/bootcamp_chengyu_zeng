"""Reusable, non-mutating data-cleaning functions for Stage 06."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

import pandas as pd


def _require_columns(frame: pd.DataFrame, columns: Sequence[str]) -> list[str]:
    selected = list(columns)
    missing = [column for column in selected if column not in frame.columns]
    if missing:
        raise KeyError(f"Columns not found in DataFrame: {missing}")
    return selected


def _require_numeric(frame: pd.DataFrame, columns: Sequence[str]) -> None:
    non_numeric = [
        column for column in columns if not pd.api.types.is_numeric_dtype(frame[column])
    ]
    if non_numeric:
        raise TypeError(f"Columns must be numeric: {non_numeric}")


def fill_missing_median(
    frame: pd.DataFrame,
    columns: Sequence[str] | None = None,
) -> pd.DataFrame:
    """Return a copy with missing numeric values filled by column medians.

    When ``columns`` is omitted, all numeric columns containing missing values
    are selected. A column containing only missing values raises an error
    because its median is undefined.
    """

    result = frame.copy(deep=True)
    selected = (
        _require_columns(result, columns)
        if columns is not None
        else result.select_dtypes(include="number")
        .columns[result.select_dtypes(include="number").isna().any()]
        .tolist()
    )
    _require_numeric(result, selected)

    for column in selected:
        median = result[column].median(skipna=True)
        if pd.isna(median):
            raise ValueError(
                f"Cannot compute a median for all-missing column: {column}"
            )
        result[column] = result[column].fillna(median)

    return result


def drop_missing(
    frame: pd.DataFrame,
    threshold: float = 0.5,
    *,
    axis: Literal["columns", "rows"] = "columns",
) -> pd.DataFrame:
    """Drop columns or rows whose missing fraction is greater than ``threshold``.

    A fraction exactly equal to the threshold is retained. The function is
    non-mutating and resets the row index when rows are removed.
    """

    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1 inclusive")
    if axis not in {"columns", "rows"}:
        raise ValueError("axis must be either 'columns' or 'rows'")

    if axis == "columns":
        keep_columns = frame.columns[frame.isna().mean(axis=0) <= threshold]
        return frame.loc[:, keep_columns].copy()

    keep_rows = frame.isna().mean(axis=1) <= threshold
    return frame.loc[keep_rows].copy().reset_index(drop=True)


def normalize_data(
    frame: pd.DataFrame,
    columns: Sequence[str],
    *,
    method: Literal["minmax", "zscore"] = "minmax",
) -> pd.DataFrame:
    """Return a copy with selected numeric columns normalized.

    ``minmax`` maps non-constant columns to [0, 1]. ``zscore`` uses the
    population standard deviation (``ddof=0``). Constant columns are mapped to
    0.0 for either method. Missing values must be handled before normalization.
    """

    result = frame.copy(deep=True)
    selected = _require_columns(result, columns)
    _require_numeric(result, selected)
    if method not in {"minmax", "zscore"}:
        raise ValueError("method must be either 'minmax' or 'zscore'")

    columns_with_missing = [
        column for column in selected if result[column].isna().any()
    ]
    if columns_with_missing:
        raise ValueError(
            f"Fill or drop missing values before normalization: {columns_with_missing}"
        )

    for column in selected:
        values = result[column].astype("float64")
        if method == "minmax":
            denominator = values.max() - values.min()
            result[column] = (
                0.0 if denominator == 0 else (values - values.min()) / denominator
            )
        else:
            standard_deviation = values.std(ddof=0)
            result[column] = (
                0.0
                if standard_deviation == 0
                else (values - values.mean()) / standard_deviation
            )

    return result
