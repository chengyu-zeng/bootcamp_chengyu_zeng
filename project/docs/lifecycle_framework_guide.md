# Lifecycle Framework Guide

| Course stage | Where the work lives | Decision or result recorded there |
|---|---|---|
| Stage 00 - Pre-class setup | `homework/homework00/python_tutorial.ipynb` | Verified the basic Python/Jupyter workflow before project work began. |
| Stage 01 - Problem framing | `homework/homework01/README.md`; `project/README.md` | Defined the portfolio risk manager, after-close decision window, SPY high-volatility target, and no-auto-trade boundary. |
| Stage 02 - Tooling setup | `project/.env.example`; `project/requirements.txt`; `project/notebooks/00_project_setup.ipynb` | Separated local configuration from Git and recorded reproducible dependencies. |
| Stage 03 - Python fundamentals | `project/notebooks/python_fundamentals_summary.ipynb`; `project/src/utils.py` | Established reusable tabular-data helpers and executable notebook conventions. |
| Stage 04 - Data acquisition | `project/src/ingestion.py`; `project/data/raw/`; `project/docs/data_sources.md` | Retrieved and retained timestamped, documented Nasdaq SPY daily source snapshots. |
| Stage 05 - Data storage | `project/src/storage.py`; `project/docs/data_storage.md`; `project/data/processed/spy_ohlcv_nasdaq_*.parquet` | Stored a typed Parquet derivative and verified round-trip integrity. |
| Stage 06 - Data preprocessing | `project/src/cleaning.py`; `project/docs/preprocessing.md`; `cleaning_report_*.json` | Applied deterministic schema, date, range, and duplicate checks without silent imputation. |
| Stage 07 - Outlier analysis | `project/src/outliers.py`; `project/docs/outliers.md`; `spy_return_outlier_flags_*.parquet` | Flagged and retained extreme return days; used filtered/winsorized outputs only as sensitivity diagnostics. |
| Stage 08 - Exploratory analysis | `project/src/eda.py`; `project/notebooks/spy_eda.ipynb`; `project/reports/spy_eda_*.png` | Documented distributions, time variation, and relationships without making causal claims. |
| Stage 09 - Feature engineering | `project/src/features.py`; `project/docs/feature_definitions.md`; `spy_feature_candidates_*.parquet` | Built end-of-day, leakage-aware candidate features and preserved the shifted outcome separately. |
| Stage 10A - Linear-model practice | `homework/homework10a/` | Practised the linear-model workflow in the self-contained course exercise. |
| Stage 10B - Classification modeling | `project/src/modeling.py`; `project/notebooks/spy_modeling.ipynb`; `project/docs/modeling.md` | Fit a chronological, class-balanced logistic baseline and selected the cutoff on validation data. |
| Stage 11 - Evaluation | `project/src/evaluation.py`; `project/notebooks/spy_evaluation.ipynb`; `project/docs/evaluation.md` | Reported held-out PR-AUC uncertainty, cutoff sensitivity, and volatility-regime failures. |
| Stage 12 - Results delivery | `project/src/reporting.py`; `project/reports/spy_risk_alert_stakeholder_report.md`; `project/docs/reporting.md` | Converted technical output into a decision memo with assumptions, risks, and an alternate cutoff. |
| Stage 13 - Productization | `project/app.py`; `project/src/productization.py`; `project/model/spy_risk_alert_model.pkl`; `project/docs/stakeholder_handoff.md` | Packaged the approved model for a validated localhost API and technical/stakeholder handoff. |
| Stage 14 - Deployment and monitoring | `project/src/monitoring.py`; `project/docs/monitoring_plan.md`; `project/docs/handoff_plan.md` | Defined Data, Model, System, and Business thresholds, owners, escalation, and rollback controls. |
| Stage 15 - Orchestration | `project/src/run_step.py`; `project/docs/orchestration_plan.md`; `project/logs/` | Mapped the DAG and exposed idempotent stakeholder-report generation as a logged CLI step. |
| Stage 16 - Lifecycle review | `project/docs/lifecycle_framework_guide.md`; `project/docs/project_summary.md`; `project/README.md` | Completed the repository map, nontechnical summary, final run instructions, and closure review. |
