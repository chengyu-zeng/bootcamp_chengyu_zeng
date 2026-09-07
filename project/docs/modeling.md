# Stage10 Modeling Baseline

The project uses a chronological 60% train / 20% validation / 20% future-test split. The training-period 90th percentile of `next_day_abs_return` defines the high-volatility label and remains fixed for validation/test.

Features include Stage09 end-of-day candidates plus time-safe prior return, five-day mean absolute return, ten-day return volatility, and five-day momentum. A `StandardScaler` and class-balanced `LogisticRegression` are fit only on training observations. Two regularization values are compared by validation PR-AUC; the alert cutoff maximizes validation F1.

This baseline does **not** meet the provisional recall-at-alert-rate target on validation. That limitation, regime instability, class imbalance, and threshold sensitivity must remain visible in later evaluation; it is not a deployment recommendation.
