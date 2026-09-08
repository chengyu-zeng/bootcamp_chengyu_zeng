# Stage15 Orchestration Plan

## Pipeline tasks and boundaries

| Task | Real input(s) | Output / checkpoint | Depends on | Idempotent? |
|---|---|---|---|---|
| 1. Acquire or select snapshot | `data/raw/api_nasdaq_spy_daily_*.csv`, provider metadata | named raw CSV and `data/raw/ingestion_manifest_*.json` | none | Yes when reusing a named snapshot; a deliberate refresh creates a new timestamped snapshot. |
| 2. Typed storage | named raw CSV | `data/processed/spy_ohlcv_nasdaq_*.parquet` | 1 | Yes; deterministic overwrite for the same snapshot. |
| 3. Clean and validate | Stage05 Parquet | `spy_ohlcv_preprocessed_*.parquet`, `cleaning_report_*.json` | 2 | Yes; fails rather than imputing invalid OHLCV values. |
| 4. Outlier diagnostics | preprocessed Parquet | `spy_return_outlier_flags_*.parquet`, sensitivity CSV, analysis JSON | 3 | Yes; flags are retained and deterministic. |
| 5. Explore and engineer features | retained Stage04 observations | EDA CSVs/charts and `spy_feature_candidates_*.parquet` | 4 | Yes; EDA and feature construction can run in parallel after outlier flags exist. |
| 6. Fit chronological baseline | feature candidates | modeling frame, validation/test metric CSVs, saved model artifact | 5 | Yes for the fixed snapshot, parameters, and random seed. |
| 7. Evaluate and deliver | test predictions and Stage10 metrics | bootstrap/scenario/subgroup CSVs, evaluation chart, stakeholder report | 6 | Yes; evaluation precedes report generation. |
| 8. Productize and monitor | saved model, reports, docs | `model/spy_risk_alert_model.pkl`, API contract, monitoring and handoff plans | 6 and 7 | Yes; it packages approved outputs without refitting. |

## Dependencies and execution shape

```text
1 Raw snapshot -> 2 Storage -> 3 Cleaning -> 4 Outlier flags
                                             |-> 5a EDA
                                             |-> 5b Features -> 6 Baseline -> 7 Evaluation -> Report
                                                                                |-> 8 API/model artifact + monitoring handoff
```

EDA and feature construction are the only useful parallel branch at current scope. Keep raw input immutable; each processed output is a checkpoint keyed to the source timestamp. `project/notebooks/project_pipeline.ipynb` remains the full manual integration test. `src/run_step.py --stage stakeholder-report` is the reusable scheduled-step candidate: it rebuilds only the final report from persisted Stage10/11 checkpoints.

## Logging, failure, and retry policy

CLI step logs go to `logs/orchestration.log` and stdout with stage, timestamp, and output checkpoint. The raw manifest and each timestamped processed artifact are durable checkpoints; the model artifact and report are final checkpoints. Fail fast on schema, missing-file, or validation errors: these require analyst investigation, not blind retries. Retry network acquisition at most three times with increasing delay only for transient provider/connection errors. Do not retry a model or report step until its missing upstream checkpoint is restored. Escalate data contract failures to the risk analyst, API failures to platform on-call, and model/business breaches to the model owner and portfolio risk manager under `docs/monitoring_plan.md`.

## Right-sized automation

Automate the after-close reuse of a validated raw snapshot, processing, report rebuild, and logging once a schedule exists. Keep data refresh, model retraining, cutoff changes, hedge analysis, and rollback approval manual: each can materially alter a risk decision and needs documented human sign-off. Airflow/Prefect, auto-trading, and automatic retraining are intentionally out of scope for this course project.
