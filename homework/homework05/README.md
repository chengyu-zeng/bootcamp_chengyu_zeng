# Stage 05: Data Storage

This homework implements a reusable storage layer for the **SPY Next-Day High-Volatility Risk Alert** project. It reuses the validated SPY OHLCV snapshot acquired in Stage 04, stores the same typed DataFrame as both CSV and Parquet, reloads each file, and verifies shape, values, null counts, column order, and critical dtype categories.

## Deliverables

```text
homework/homework05/
├── .env.example
├── README.md
├── homework05_data-storage_submission.ipynb
├── data/
│   ├── raw/
│   │   └── spy_ohlcv_<YYYYMMDD-HHMM>.csv
│   └── processed/
│       └── spy_ohlcv_<YYYYMMDD-HHMM>.parquet
└── src/
    ├── __init__.py
    └── storage.py
```

The local `.env` is intentionally absent from the tree above because it is covered by the repository-level `.gitignore`. Only `.env.example`, which contains no secret values, is committed.

## Data Storage

### Folder structure

- `data/raw/` contains the portable CSV snapshot. This layer preserves a straightforward, human-readable interchange copy and is not manually edited after creation.
- `data/processed/` contains the corresponding Parquet file. This layer is ready for efficient typed analytical reads in later stages.

### Formats and rationale

- **CSV** is widely supported, easy to inspect, and appropriate for a small raw snapshot. It does not preserve types on its own, so `read_df` accepts explicit `parse_dates` and `dtype` arguments.
- **Parquet** is columnar, compact, and preserves pandas-compatible schema information such as datetime, floating-point, and integer types. The submission uses PyArrow with Snappy compression.

The two files contain the same 2,512 SPY observations and six columns. They are stored in separate folders to demonstrate the course convention; Stage 06 will introduce substantive preprocessing rather than claiming that a format conversion itself cleans the data.

### Environment-driven paths

The notebook loads its local `.env` explicitly and resolves relative paths against `homework05`, independent of the launch directory:

```dotenv
DATA_DIR_RAW=data/raw
DATA_DIR_PROCESSED=data/processed
```

`src/storage.py` provides:

- `detect_format(path)` to route `.csv`, `.parquet`, `.parq`, and `.pq` suffixes;
- `write_df(frame, path)` to create missing parent directories and atomically write either format;
- `read_df(path)` to check existence and reload either format; and
- `validate_roundtrip(...)` to produce explicit shape, column, null-count, value, and dtype checks.

If neither PyArrow nor fastparquet is installed, Parquet operations raise a clear message with an installation command. Unsupported suffixes and missing files also fail with specific errors.

## Environment and Reproduction

Continue with the Stage 02 `fe-course` environment and add PyArrow:

```bash
conda activate fe-course
python -m pip install pyarrow
```

The submitted run used Python 3.11, pandas 3.0.5, and pyarrow 25.0.1. Execute from the repository root:

```bash
conda run -n fe-course jupyter nbconvert \
  --to notebook \
  --execute \
  --inplace \
  homework/homework05/homework05_data-storage_submission.ipynb
```

Each run creates timestamped output paths. The notebook selects the most recent Stage 04 SPY CSV by filename, checks its schema before writing, and fails rather than generating substitute data when the input is missing.

## Assumptions and Risks

- The latest filename-sorted Stage 04 `api_NASDAQ_SPY_*.csv` is the intended input snapshot.
- CSV readers must receive explicit schema hints to restore datetimes reliably; Parquet schema preservation is more automatic but depends on a compatible engine.
- Timestamp precision is one minute, matching the assignment example. Repeated runs within the same minute intentionally replace the same logical snapshot instead of creating ambiguous duplicates.
- Parquet files are not guaranteed to be readable by every older engine version. The required PyArrow dependency and version are documented for reproducibility.
- `data/processed/` in this stage denotes a typed analytical format, not cleaned or feature-engineered data.

## AI Assistance Disclosure

An AI assistant helped implement and validate this Stage 05 submission. The student is responsible for understanding the raw/processed convention, CSV-versus-Parquet trade-offs, environment-driven path resolution, and each storage utility.
