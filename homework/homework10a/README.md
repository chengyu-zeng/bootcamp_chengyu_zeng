# Stage 10A: Modeling - Linear Regression

This self-contained homework uses the committed Stage09 SPY feature snapshot to build a chronological linear-regression baseline for `next_day_abs_return`. It is a diagnostic continuous-risk model, not the final high-volatility alert classifier.

## Design

- Input: 2,512-row Stage09 feature snapshot copied into `data/raw/`.
- Target: continuous next-day absolute close-to-close return.
- Split: earliest 80% for training; most recent 20% for testing. No shuffle.
- Baseline features: absolute return, intraday range, log-volume change, and five-day rolling volatility at date `t`.
- Diagnostic variant: adds intraday-range squared and the existing stress interaction. It remains linear in coefficients.

## Deliverables

- `homework10a_modeling-linear-regression_submission.ipynb`: reproducible fit, metrics, residual diagnostics, and interpretation.
- `data/processed/linear_regression_metrics.csv`: held-out metrics for both specifications.
- `reports/linear_regression_diagnostics.png`: residual-vs-fitted, histogram, QQ, and lag-1 residual diagnostics.

## Interpretation boundary

This model uses only information available at the close of date `t` to predict the continuous outcome at `t+1`. Its held-out metrics are diagnostic evidence, not proof of causality or permission to deploy a risk alert. The project will use a time-aware classification pipeline for the final high-volatility decision.
