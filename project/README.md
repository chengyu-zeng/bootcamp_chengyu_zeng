# SPY Next-Day High-Volatility Risk Alert

This directory is the integrated project workspace. It will build a reproducible end-of-day workflow that estimates the probability of a high-volatility SPY session on the next trading day and supports a portfolio risk manager's decision to request additional review, stress testing, or hedge analysis. The decision window is after the U.S. market close and before the next market open; a high-risk result prompts review rather than an automated trade.

The primary stakeholder and decision owner is a portfolio risk manager. A risk analyst operates the workflow, validates inputs, and prepares the daily risk note; a portfolio manager is a secondary consumer. The project is predictive, not causal: using only information available by the current close, it estimates whether the next session's absolute SPY close-to-close return will exceed the 90th percentile calculated from training history. Its output is a probability, high/normal alert, data-quality status, and concise explanation.

## Stage 01 Decision Framing

The primary evaluation metric is PR-AUC. A validation-selected alert threshold will provisionally target at least 60% recall of high-volatility sessions with an alert rate no greater than 20%; precision, calibration, and chronological out-of-sample performance will also be reported. These targets are decision criteria to validate with the stakeholder, not fixed economic guarantees.

The first version is limited to daily SPY data and excludes intraday order-book data, options data, portfolio holdings, transaction costs, and hedge execution. Key risks include market-regime instability, rare-event uncertainty, threshold sensitivity, data revisions or quality failures, and look-ahead leakage. Raw snapshots, source metadata, timestamped features, and chronological splits will support reproducibility and auditability.

## Goals → Lifecycle → Deliverables

| Goal | Lifecycle Stage | Deliverable |
|---|---|---|
| Define the decision, stakeholder, scope, and risks | Stage 01 — Problem Framing | This README and stakeholder memo |
| Establish reproducible tooling and configuration | Stage 02 — Tooling Setup | Environment specification, `.env.example`, project scaffold |
| Demonstrate reusable data handling | Stage 03 — Python Fundamentals | `python_fundamentals_summary.ipynb` and reusable `src/utils.py` helpers |
| Acquire documented market data | Stage 04 — Data Acquisition | `project_pipeline.ipynb`, validated SPY raw snapshot, manifest, and ingestion code |
| Preserve inputs and derived datasets | Stage 05 — Data Storage | Env-driven IO, validated Parquet derivative, and storage documentation |
| Create an analysis-ready time series | Stage 06 — Data Preprocessing | Deterministic cleaning, report, and preprocessed Parquet |
| Test extreme-observation choices | Stage 07 — Outlier Analysis | Outlier analysis and treatment decision record |
| Understand time-series behavior | Stage 08 — EDA | EDA notebook, charts, and findings |
| Build information-available predictors | Stage 09 — Feature Engineering | Leakage-safe feature module and definitions |
| Estimate next-session event risk | Stage 10 — Modeling | Baselines, candidate models, risk probabilities |
| Validate reliability and uncertainty | Stage 11 — Evaluation & Risk Communication | Chronological backtest, calibration, risk metrics |
| Deliver the decision-support output | Stage 12 — Results Reporting & Delivery | Daily risk table, documentation, stakeholder presentation |

Detailed Stage 01 evidence remains in [the scoping README](../homework/homework01/README.md) and [the stakeholder memo](../homework/homework01/docs/stakeholder_context_memo.md).

## Project Structure

```text
project/
├── .env.example
├── requirements.txt
├── data/
│   ├── processed/
│   └── raw/
├── docs/
│   ├── data_sources.md
│   ├── data_storage.md
│   ├── eda.md
│   ├── feature_definitions.md
│   ├── outliers.md
│   └── preprocessing.md
├── model/
├── notebooks/
│   ├── 00_project_setup.ipynb
│   ├── python_fundamentals_summary.ipynb
│   ├── project_pipeline.ipynb
│   └── spy_eda.ipynb
├── reports/
└── src/
    ├── config.py
    ├── cleaning.py
    ├── eda.py
    ├── ingestion.py
    ├── outliers.py
    ├── storage.py
    └── utils.py
```

- `data/raw/`: Timestamped immutable-style source snapshots and acquisition manifests.
- `data/processed/`: Reproducible cleaned and feature-ready datasets.
- `notebooks/`: Ordered, executable analysis notebooks; `00_project_setup.ipynb` verifies this environment and configuration, `python_fundamentals_summary.ipynb` demonstrates Stage 03 code with toy data, and the cumulative `project_pipeline.ipynb` begins ingestion in Stage 04.
- `src/`: Reusable ingestion, validation, cleaning, feature, and evaluation code; `config.py` loads local configuration, `ingestion.py` acquires and validates raw SPY data, and `utils.py` provides general tabular-data helpers.
- `docs/`: Stakeholder memos, assumptions, risks, and decision records.
- `reports/`: Generated tables, charts, and presentation-ready outputs.
- `model/`: Serialized model artifacts and model metadata when modeling begins.

## Environment and Secrets

Stage 02 uses the `fe-course` Conda environment with Python 3.11.15. `requirements.txt` is a dependency snapshot generated from that environment; re-freeze it whenever project dependencies change. Configuration values are read from a local `.env` copied from `.env.example`; the real `.env` is excluded from Git. Raw data, processed data, code, and documentation remain separated so that each result can be reproduced and audited.

## Data Storage

- `data/raw/` holds timestamped, immutable-style provider snapshots and manifests. It is never used for manually edited or derived outputs.
- `data/processed/` holds reproducible derivatives. Stage05 writes a Snappy-compressed Parquet representation of a named raw SPY snapshot; it is a typed storage representation, not a claim that the data are already cleaned.
- `src.config` resolves `DATA_DIR_RAW` and `DATA_DIR_PROCESSED` from the ignored local `.env`; `src.storage` reads/writes CSV or Parquet by suffix and validates round-trip shape, schema, null counts, values, and critical dtypes.
- See [data storage conventions](docs/data_storage.md) for format rationale, lineage, and reproduction steps.

## Data Preprocessing

- Stage06 reads the named Stage05 Parquet derivative, performs canonical schema/type/date/order/duplicate/range checks, and writes a new preprocessed Parquet plus JSON cleaning report.
- The policy deliberately fails on missing or invalid OHLCV values rather than imputing or silently dropping them. Outlier treatment is deferred to Stage07.
- Raw data remain unadjusted and unchanged. No global scaling is performed; any future scaler must fit only on training data.
- See the [preprocessing policy](docs/preprocessing.md) for lineage, assumptions, and non-actions.

## Outlier Analysis

- Stage07 calculates close-to-close daily returns from the Stage06 dataset and adds IQR (`k=1.5`) and z-score (`|z| > 3`) review flags without deleting market dates.
- The default decision is flag-and-retain. Filtered and 5%/95% winsorized variants are sensitivity diagnostics, not replacement production data.
- Full-snapshot thresholds are descriptive only; future modeling will estimate any threshold or boundary on training data alone.
- See the [outlier policy](docs/outliers.md) for definitions, lineage, assumptions, and risks.

## Exploratory Data Analysis

- Stage08 profiles the retained Stage07 data, including structural missingness, distributions, categorical balance, relationships, correlation, and time-series behavior.
- The reusable `src.eda` helper and `spy_eda.ipynb` separate descriptive findings from leakage-safe future feature decisions.
- See the [EDA policy](docs/eda.md) for data lineage, interpretation limits, and Stage09 implications.

## Feature Engineering

- Stage09 converts Stage08 observations into end-of-day candidate features: return magnitude, intraday range, log-volume change, five-day rolling volatility, a stress interaction, and one-hot weekday fields.
- Every `*_t` feature uses only information available after date `t` closes. `next_day_abs_return` is a shifted continuous outcome, not a feature; its terminal missing value and warm-up missing values are preserved.
- The high-volatility event threshold, train-only transformations, feature selection, and chronological model evaluation remain Stage10+ work. See [feature definitions and leakage policy](docs/feature_definitions.md).

## Modeling Baseline

- Stage10 uses chronological train/validation/test blocks, a training-only high-volatility threshold, and a `StandardScaler` plus class-balanced logistic-regression pipeline.
- Validation chooses regularization by PR-AUC and the operating cutoff by F1; the provisional recall/alert-rate target is reported as an unmet model limitation, not hidden. See [modeling policy](docs/modeling.md).

## Current Status

The Stage 02 tooling scaffold and Stage 03 foundational utilities are in place. Stage 04 adds ingestion and raw SPY snapshots; Stage 05 adds validated storage; Stage 06 adds deterministic preprocessing; Stage 07 adds return-outlier review and sensitivity analysis; Stage 08 adds reusable EDA summaries and documented visual analysis; Stage09 adds leakage-aware, information-available feature candidates; Stage10 adds a chronological classification baseline and its risk-aware diagnostics. Later stages will strengthen evaluation, calibration, and reporting.
