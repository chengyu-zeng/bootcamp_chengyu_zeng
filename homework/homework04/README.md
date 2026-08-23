# Stage 04: Data Acquisition and Ingestion

This homework acquires two raw datasets that support the Stage 01 **SPY Next-Day High-Volatility Risk Alert** project:

1. daily SPY open, high, low, close, and volume observations from Nasdaq's public JSON endpoint; and
2. the current S&P 500 constituents table from Wikipedia, parsed from `table#constituents` with BeautifulSoup.

Both pulls are converted to typed pandas DataFrames, validated, and saved as timestamped CSV snapshots. A JSON manifest records source metadata, validation summaries, file sizes, and SHA-256 checksums.

## Deliverables

```text
homework/homework04/
├── .env.example
├── README.md
├── homework04_data-acquisition-and-ingestion_submission.ipynb
├── data/
│   └── raw/
│       ├── api_NASDAQ_SPY_<YYYYMMDD-HHMM>.csv
│       ├── ingestion_manifest_<YYYYMMDD-HHMM>.json
│       └── scrape_WIKIPEDIA_SP500_CONSTITUENTS_<YYYYMMDD-HHMM>.csv
└── src/
    ├── __init__.py
    └── ingestion.py
```

The local `.env` exists beside `.env.example` but is excluded by the repository-level `.gitignore`. No API key is required for the selected Nasdaq and Wikipedia sources. The Alpha Vantage variable remains as a safe template for later use.

## Environment

Continue with the Stage 02 `fe-course` environment. Stage 04 uses `pandas`, `requests`, `beautifulsoup4`, and `python-dotenv`, all of which are present in the working environment.

```bash
conda activate fe-course
python -m pip install pandas requests beautifulsoup4 python-dotenv
```

## Reproduce the Submission

From the repository root, execute the notebook top to bottom:

```bash
conda run -n fe-course jupyter nbconvert \
  --to notebook \
  --execute \
  --inplace \
  homework/homework04/homework04_data-acquisition-and-ingestion_submission.ipynb
```

Each run retrieves live source data and writes a timestamped raw snapshot. Consequently, row counts and the latest available trading date can change. The committed files preserve the exact data used in the submitted run.

## Validation Performed

- Nasdaq response status and non-empty `tradesTable.rows`
- required SPY columns: `date`, `open`, `high`, `low`, `close`, `volume`
- parsed datetime and numeric dtypes
- explicit rejection if more than 1% of source rows have incomplete OHLCV; isolated incomplete rows are counted in metadata and excluded from the typed snapshot
- missing values, duplicate dates, positive prices, nonnegative volume, and OHLC range consistency
- required constituents columns, at least 400 rows, nonblank text fields, unique tickers, positive numeric CIK values, and at least eight GICS sectors

## Assumptions and Risks

- Nasdaq's public website endpoint is not a contractual data service. Rate limits, access policies, schema, or availability can change.
- The Nasdaq extract is unadjusted OHLCV. Later return calculations must decide how to handle distributions and corporate actions and should not silently treat these values as adjusted prices.
- In the submitted pull, Nasdaq reported `N/A` volume for 2026-04-20. The parser recorded the date and excluded that single incomplete row; it is not imputed or silently converted to zero.
- The Wikipedia selector and column names may change. The code fails loudly when the expected table or schema is absent instead of substituting fabricated data.
- The constituents table is a current snapshot, not historical index membership. Using it to reconstruct past membership would introduce survivorship bias.
- Source data may be revised after the snapshot. The timestamped raw files and checksums make the submitted inputs auditable but do not guarantee future source equality.
- The data supports predictive analysis and quality checks; it does not establish a causal explanation for volatility or constitute investment advice.

## AI Assistance Disclosure

An AI assistant helped implement and validate this Stage 04 submission. The student is responsible for reviewing the source permissions, understanding the HTTP/parsing/validation logic, and being able to reproduce and explain every deliverable.
