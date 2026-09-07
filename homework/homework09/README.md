# Stage 09: Feature Engineering

This homework turns Stage08 EDA observations into reproducible, leakage-aware SPY feature candidates. It uses a committed 2,512-row Stage08 SPY snapshot and deliberately keeps the continuous `next_day_abs_return` as a diagnostic outcome rather than prematurely fixing the future high-volatility classification threshold.

## Features and EDA Rationale

| Feature | EDA rationale | Availability |
|---|---|---|
| `abs_return_t` | Return tails and volatility clustering | Known after date `t` close |
| `intraday_range_t` | Range rises during pressure sessions | Known after date `t` close |
| `log_volume_change_t` | Volume changes may reflect unusual activity | Known after date `t` close |
| `rolling_volatility_5_t` | Recent volatility regime | Uses returns through date `t` only |
| `stress_interaction_t` | Large return plus large range captures stress | Uses date `t` only |
| `weekday_*` | One-hot categorical calendar representation | Date `t` is known |

The notebook creates pairwise correlations to the shifted continuous outcome. They are exploratory associations, not causal claims or proof of predictive value. The first return/volume-change row and initial rolling-window rows are structural warm-up missingness; the final target row is missing because the retained snapshot has no next date.

## Deliverables

- `src/features.py`: reusable feature builder and correlation helper.
- `homework09_feature-engineering_submission.ipynb`: implementation, correlations, visual check, and interpretation.
- `data/processed/spy_feature_candidates.csv` and `feature_target_correlations.csv`.
- `reports/feature_target_correlations.png`.

## Leakage Rules

Features at date `t` may use data through date `t` close. `next_day_abs_return` uses `shift(-1)` and is outcome-only. The eventual 90th-percentile high-volatility classification threshold must be estimated from training history only in later modeling work.
