# Stage 08: Exploratory Data Analysis

This homework performs a comprehensive EDA on the real SPY OHLCV dataset acquired in Stage 04 and stored as Parquet in Stage 05. It profiles numeric, categorical, and datetime fields; examines distributions and relationships; audits the trading-date axis; compares daily and monthly views; and converts findings into concrete implications for Stage 09 feature engineering and later chronological modeling.

## Deliverables

```text
homework/homework08/
├── README.md
├── homework08_exploratory-data-analysis_submission.ipynb
├── data/
│   ├── raw/
│   │   └── spy_ohlcv_stage05_snapshot.parquet
│   └── processed/
│       ├── eda_categorical_summary.csv
│       ├── eda_column_profile.csv
│       ├── eda_correlation_matrix.csv
│       ├── eda_monthly_profile.csv
│       └── eda_numeric_summary.csv
├── reports/
│   ├── categorical_profiles.png
│   ├── correlation_heatmap.png
│   ├── distributions.png
│   ├── relationships.png
│   └── time_series.png
└── src/
    ├── __init__.py
    └── eda.py
```

## Dataset and EDA Scope

The committed raw snapshot contains 2,512 SPY trading sessions from 2016-08-23 through 2026-08-21 with `open`, `high`, `low`, `close`, and `volume`. The notebook validates this copy against the latest Stage 05 Parquet file when that prerequisite is available.

EDA-only columns are derived in memory:

- close-to-close `daily_return` and `abs_return`;
- `(high - low) / open` as `intraday_range`;
- close-to-open return and log volume;
- trailing 21-session annualized volatility;
- categorical `return_direction` and `weekday_name`.

These are exploratory definitions, not finalized Stage 09 features. In particular, any rolling or threshold parameters used for modeling must be computed without future information.

## Reusable Summary Helper

`src/eda.py` provides `eda_summary(df)`, which returns:

- overall shape, missing-cell, duplicate-row, and memory statistics;
- per-column dtype, analytical role, missingness, cardinality, and dominance;
- numeric `.describe()` output plus skewness and kurtosis;
- counts and proportions for every categorical field;
- datetime coverage, uniqueness, and ordering checks; and
- attention flags for missingness, high missingness, near-zero variance, or one dominant category.

Datetime fields are profiled separately rather than producing thousands of unhelpful date value-count rows.

## Top Findings

1. **Return tails are much heavier than a normal benchmark.** Daily-return excess kurtosis is about 14.7, while absolute return, intraday range, volume, and 21-session volatility are strongly right-skewed. Tail-aware validation and robust scaling are more appropriate than assuming Gaussian behavior.
2. **Volatility and range contain related but nonidentical information.** Absolute daily return correlates about 0.72 with intraday range and about 0.54 with log volume. These variables can support Stage 09 lagged and rolling risk features, but correlated features should be checked for redundancy.
3. **Risk is clustered in time.** The rolling-volatility plot shows clear regimes, with the strongest cluster in March 2020 and additional elevated periods in 2022 and 2025. A random split would mix regimes and overstate generalization; Stage 10b needs chronological splits and regime-aware reporting.

The closing-price level rises substantially over the sample and is nonstationary, while daily returns fluctuate around a far more stable location. Price levels should not be used directly as if they were stationary predictors.

## Assumptions and Risks

- Nasdaq supplied unadjusted OHLCV. Close-to-close returns around distributions or corporate actions may not equal total returns; later work should select and document an adjustment policy.
- The first daily return and the first 21 rolling-volatility values are structurally missing. They should be dropped only after features and the next-session target are aligned, not imputed with future-aware statistics.
- The date axis is sorted and unique. Weekday gaps include expected U.S. market holidays, so a missing weekday is not automatically a data error. Rolling windows are interpreted as trading sessions.
- `return_direction` and `weekday_name` are created for categorical EDA. Weekday counts mainly reflect the exchange calendar and should not be interpreted causally.
- Correlation is contemporaneous and does not establish predictive value or causality. Stage 09 must lag features before using them to predict the next session.
- The most recent observations and source values may later be revised. The committed snapshot preserves the inputs used for this submission.

## Implications for Next Step

- Engineer lagged daily returns, absolute returns, intraday range, log-volume changes, and rolling volatility using prior sessions only.
- Build the next-session high-volatility target with an explicit shift and estimate its percentile threshold on training data only.
- Prefer returns or normalized ratios over raw price levels; consider robust transforms for volume and range.
- Preserve extreme sessions because they are central to the risk-alert objective; add regime and sensitivity diagnostics instead of deleting them mechanically.
- Use chronological train/validation/test splits and verify that every rolling feature respects date order and required warm-up periods.

## Reproduce the Submission

Continue with the `fe-course` environment and add seaborn if needed:

```bash
conda activate fe-course
python -m pip install seaborn
```

The submitted run used Python 3.11, NumPy 2.4.6, pandas 3.0.5, SciPy 1.17.1, matplotlib 3.11.1, seaborn 0.13.2, and PyArrow 25.0.1. Execute from the repository root:

```bash
conda run -n fe-course jupyter nbconvert \
  --to notebook \
  --execute \
  --inplace \
  homework/homework08/homework08_exploratory-data-analysis_submission.ipynb
```

Processed tables and plots are recreated deterministically from the committed raw snapshot.

## AI Assistance Disclosure

An AI assistant helped implement and validate this Stage 08 submission. The student is responsible for understanding each visual, checking the source data assumptions, and translating EDA findings into leakage-safe feature and evaluation choices.
