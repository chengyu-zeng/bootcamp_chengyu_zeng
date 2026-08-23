# SPY Next-Day High-Volatility Risk Alert

This directory is the integrated project workspace introduced in Stage 02. The project will build a reproducible end-of-day workflow that estimates the probability of a high-volatility SPY session on the next trading day and supports a portfolio risk manager's decision to request additional review, stress testing, or hedge analysis.

The detailed problem definition, stakeholder roles, success criteria, assumptions, and lifecycle mapping are documented in [the Stage 01 scoping README](../homework/homework01/README.md). The stakeholder-facing decision context is documented in [the Stage 01 memo](../homework/homework01/docs/stakeholder_context_memo.md).

## Project Structure

```text
project/
├── .env.example
├── data/
│   ├── processed/
│   └── raw/
├── docs/
├── model/
├── notebooks/
├── reports/
└── src/
```

- `data/raw/`: Immutable source snapshots and acquisition metadata.
- `data/processed/`: Reproducible cleaned and feature-ready datasets.
- `notebooks/`: Ordered, executable analysis notebooks.
- `src/`: Reusable ingestion, validation, cleaning, feature, and evaluation code.
- `docs/`: Stakeholder memos, assumptions, risks, and decision records.
- `reports/`: Generated tables, charts, and presentation-ready outputs.
- `model/`: Serialized model artifacts and model metadata when modeling begins.

## Environment and Secrets

Stage 02 uses the `fe-course` Conda environment with Python 3.11. Configuration values will be read from a local `.env` copied from `.env.example`; the real `.env` is excluded from Git. Raw data, processed data, code, and documentation will remain separated so that each result can be reproduced and audited.

## Current Status

The tooling scaffold is in place. Data ingestion begins in Stage 04, with storage, preprocessing, risk analysis, EDA, and feature engineering added in later stages.
