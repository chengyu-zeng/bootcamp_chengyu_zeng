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
| Acquire documented market data | Stage 04 — Data Acquisition | Validated extracts, source metadata, ingestion code |
| Preserve inputs and derived datasets | Stage 05 — Data Storage | Raw/processed data conventions and versioned snapshots |
| Create an analysis-ready time series | Stage 06 — Data Preprocessing | Cleaning pipeline, validation report, processed dataset |
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
├── model/
├── notebooks/
│   ├── 00_project_setup.ipynb
│   └── python_fundamentals_summary.ipynb
├── reports/
└── src/
    ├── config.py
    └── utils.py
```

- `data/raw/`: Immutable source snapshots and acquisition metadata.
- `data/processed/`: Reproducible cleaned and feature-ready datasets.
- `notebooks/`: Ordered, executable analysis notebooks; `00_project_setup.ipynb` verifies this environment and configuration without displaying secret values, while `python_fundamentals_summary.ipynb` demonstrates Stage 03 code with toy data.
- `src/`: Reusable ingestion, validation, cleaning, feature, and evaluation code; `config.py` loads local configuration independently of the launch directory, and `utils.py` provides general tabular-data helpers.
- `docs/`: Stakeholder memos, assumptions, risks, and decision records.
- `reports/`: Generated tables, charts, and presentation-ready outputs.
- `model/`: Serialized model artifacts and model metadata when modeling begins.

## Environment and Secrets

Stage 02 uses the `fe-course` Conda environment with Python 3.11.15. `requirements.txt` is a dependency snapshot generated from that environment; re-freeze it whenever project dependencies change. Configuration values are read from a local `.env` copied from `.env.example`; the real `.env` is excluded from Git. Raw data, processed data, code, and documentation remain separated so that each result can be reproduced and audited.

## Current Status

The Stage 02 tooling scaffold and Stage 03 foundational utilities are in place. Data ingestion begins in Stage 04, with storage, preprocessing, risk analysis, EDA, and feature engineering added in later stages.
