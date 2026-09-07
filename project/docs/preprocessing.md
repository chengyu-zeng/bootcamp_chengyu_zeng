# Preprocessing Policy

## Input and Output Lineage

Stage06 reads the typed Stage05 Parquet representation of the timestamped Stage04 SPY raw snapshot. It writes a separate preprocessed Parquet file and deterministic JSON cleaning report in `data/processed/`. The raw CSV and its manifest are never modified.

## Deterministic Cleaning Policy

The pipeline keeps only the canonical OHLCV schema, reparses dates and numeric fields, verifies no missing values or duplicate dates, checks positive prices and nonnegative volume, checks OHLC consistency, and sorts by date if needed. It records input/output shapes, dtypes, missingness, sorting, rows dropped, date range, and policies in the report.

## Explicit Non-Actions

- **No price imputation:** a market-date gap, provider failure, and holiday have different meanings. Missing OHLCV causes a clear failure rather than median or forward-fill imputation.
- **No invalid-row deletion:** invalid values cause a clear failure rather than silent removal.
- **No outlier treatment:** tail events can be economically meaningful and are deferred to Stage07.
- **No global scaling:** a future scaler must be fit on training observations only, then applied unchanged to validation/test data to avoid leakage.

The data remain unadjusted OHLCV. Corporate-action and return-definition choices remain downstream preprocessing decisions and must be documented before target construction.
