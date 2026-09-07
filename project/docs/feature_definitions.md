# Stage09 Feature Definitions and Leakage Policy

## Purpose and lineage

Stage09 turns Stage08 descriptive observations about return tails, intraday range, volume changes, volatility clustering, and calendar composition into reproducible **candidate** predictors for the SPY next-day high-volatility risk alert. The input is the retained Stage07 dataset, `spy_return_outlier_flags_20260907-143336.parquet`; Stage07 flags remain review information and do not remove observations.

The generated feature table preserves one row per trading date. It is produced by `src.features.build_spy_features` and is not yet a model-ready train/test dataset. Stage10 will define chronological splits, fit any learned transforms on training data only, and convert the continuous outcome into the planned high-volatility event using a training-history threshold.

## Information timing

For a decision made after the close on trading date $t$:

$$
x_t = f(\mathcal{F}_t), \qquad y_{t+1} = |r_{t+1}|.
$$

All candidate predictors end in `_t` and use only the date-$t$ OHLCV record or prior records. `next_day_abs_return` is created with `shift(-1)` and is outcome-only. It is structurally missing on the final retained date; warm-up missingness is retained rather than filled.

| Field | Definition | Available by end of $t$ | EDA rationale |
|---|---|---:|---|
| `return_t` | Close-to-close return at $t$ | Yes | Base return series; used to derive other fields |
| `abs_return_t` | $|return_t|$ | Yes | Return tails and volatility clustering |
| `intraday_range_t` | $(high_t-low_t)/open_t$ | Yes | Session-level price pressure/range |
| `log_volume_change_t` | $\log(1+volume_t)-\log(1+volume_{t-1})$ | Yes | Unusual activity proxy |
| `rolling_volatility_5_t` | 5-day annualized sample volatility through $t$ | Yes | Recent volatility regime |
| `stress_interaction_t` | `abs_return_t × intraday_range_t` | Yes | Joint large-move/range stress candidate |
| `weekday_Monday` … `weekday_Friday` | One-hot calendar fields | Yes | Unordered categorical calendar representation |
| `next_day_abs_return` | $|return_{t+1}|$ | No — outcome only | Continuous diagnostic outcome for later target construction |

## Encoding and non-actions

Weekday is represented by five one-hot fields; it is not integer label encoded because weekdays have no numeric order. No global scaling, imputation, dropping of outlier-flagged dates, target encoding, or full-snapshot quantile threshold is performed in this stage. Pairwise Pearson correlations are saved only as a descriptive diagnostic and do not establish prediction, causation, or final feature selection.

## Reproduction and checks

Run `project/notebooks/project_pipeline.ipynb` with `REFRESH_RAW = False`. The Stage09 cell writes the feature Parquet and correlation CSV, reloads both, and verifies row preservation, structural missingness, weekday encoding, date ordering, and storage round trips. Raw source snapshots and earlier processed artifacts are not modified.
