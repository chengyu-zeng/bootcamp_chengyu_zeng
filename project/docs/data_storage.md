# Data Storage Conventions

## Folder Contract

- `data/raw/` contains timestamped source snapshots and manifests exactly as retained from acquisition. These files are not manually edited or overwritten.
- `data/processed/` contains deterministic, analysis-ready derivatives that can be recreated from a named raw snapshot and project code.

## Formats

- The Stage04 SPY source remains a CSV because it is small, portable, and easy to inspect. CSV reloads must explicitly restore `date` and numeric schema.
- The Stage05 derivative is a Snappy-compressed Parquet file because it preserves the typed table schema and is efficient for repeated analytical reads. It requires the pinned `pyarrow` engine.

## Paths and Validation

`DATA_DIR_RAW` and `DATA_DIR_PROCESSED` are read from the ignored local `.env` through `src.config`; relative values are resolved from `project/`, never from a hardcoded user path. `src.storage` routes reads and writes by suffix and validates every CSV/Parquet round trip for shape, column order, null counts, values, and critical dtype categories.

## Reproduction

The cumulative `notebooks/project_pipeline.ipynb` defaults to the latest committed Stage04 raw snapshot, so normal reruns do not create duplicate network pulls. Set `REFRESH_RAW = True` only when an intentional new acquisition is wanted. The processed Parquet filename includes the source snapshot timestamp, preserving lineage without modifying raw artifacts.
