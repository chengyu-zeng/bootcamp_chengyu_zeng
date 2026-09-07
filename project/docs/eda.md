# Exploratory Data Analysis Policy

## Scope and Lineage

Stage08 reads the retained Stage07 return-outlier Parquet and derives descriptive-only columns: daily return, absolute return, intraday range, close-to-open return, log volume, 21-session annualized rolling volatility, return direction, and weekday. It writes summary tables to `data/processed/` and visualization reports to `reports/`. Earlier snapshots are never overwritten.

## Interpretation Rules

EDA findings are hypotheses, not causal or predictive claims. Price levels trend across this history, so return and ratio views are more meaningful for distributional risk analysis. Correlation is contemporaneous and does not establish that one field predicts another. The first daily return and the first 21 rolling-volatility observations are structural warm-up missingness, not values to impute.

## Next-Stage Implications

The EDA notebook investigates tails, volatility clustering, volume/range relationships, and regime changes. Any Stage09 feature must be aligned so it uses only information available by the current close. Any Stage10 threshold, transform, or model split must be estimated chronologically using training data only. Extreme observations remain retained and are reviewed through Stage07 flags rather than deleted.
