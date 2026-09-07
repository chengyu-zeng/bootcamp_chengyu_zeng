# Stage 10B: Time Series and Classification

This self-contained homework builds a chronological SPY high-volatility classification baseline from the committed Stage09 feature snapshot. It predicts whether the next trading day's absolute return exceeds the training-period 90th percentile.

## Time-safe design

- New features: prior-day return, five-day rolling mean absolute return, ten-day rolling return standard deviation, and five-day momentum. Each uses information through date `t` only.
- Target: `next_day_abs_return > training_quantile_90`; the threshold is fit on the earlier 80% only and then fixed for future-like test observations.
- Model: `Pipeline(StandardScaler, LogisticRegression(class_weight="balanced"))` fitted only on the chronological training block.
- Metrics: accuracy, precision, recall, F1, PR-AUC, alert rate, and a confusion matrix.

## Deliverables

- `homework10b_modeling-time-series-and-classification_submission.ipynb`
- `data/processed/classification_metrics.csv`
- `reports/classification_diagnostics.png`

## Interpretation boundary

This is a reproducible baseline, not a deployed alert. Its fixed 0.50 probability cutoff is only a homework convention; the project will select an operating threshold on a separate chronological validation period, then evaluate once on an untouched future test period.
