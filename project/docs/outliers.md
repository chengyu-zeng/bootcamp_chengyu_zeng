# Outlier Analysis Policy

## Purpose and Input Lineage

Stage07 reads the Stage06 preprocessed SPY OHLCV Parquet. It derives same-day close-to-close `daily_return`, creates IQR and z-score review flags, and writes separate analysis artifacts in `data/processed/`. The Stage04 raw CSV, Stage05 storage derivative, and Stage06 preprocessed dataset are never overwritten.

## Definition and Default Decision

The primary review flag uses Tukey IQR fences on `daily_return` with `k=1.5`. A z-score flag with population standard deviation and threshold 3.0 is retained as a secondary diagnostic. The first daily return is missing by construction because no prior close exists; it is kept and unflagged.

The default action is **flag and retain**. Extreme returns can represent true crash, recovery, liquidity, or regime events that are central to a next-day high-volatility risk alert. A flag is not evidence of a bad market-data record, and it never triggers a silent row deletion.

## Sensitivity Analysis and Limits

The Stage07 table compares all returns, an IQR-filtered counterfactual, and a 5%/95% winsorized counterfactual using count, mean, median, standard deviation, minimum, and maximum. These variants quantify dependence on tail observations; they are not alternative production datasets or a claim that the lowest volatility variant is best.

Thresholds in this stage are estimated from the retained full snapshot solely for descriptive review. When modeling begins, any outlier threshold or winsorization boundary must be estimated on training observations only and applied unchanged to validation/test data to prevent future leakage.

## Risks and Follow-up

IQR is robust but may flag legitimate fat-tail returns. Z-scores assume a roughly symmetric, light-tailed distribution and can be distorted by the extremes they assess. Winsorizing preserves dates but changes tail magnitude, so it can understate tail risk. Later stages should investigate flagged dates, market regimes, and the relation between current extremes and the future target rather than discard them automatically.
