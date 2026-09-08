# Stage12 Reporting and Delivery Policy

## Audience and artifact

The primary audience is the portfolio risk manager. `reports/spy_risk_alert_stakeholder_report.md` is a decision memo for an after-close review window, not a model-development notebook or a trading instruction.

## Delivery contract

The report must state: (1) the recommendation and decision boundary, (2) held-out evidence and uncertainty, (3) at least one alternate cutoff scenario, (4) assumptions and risks, and (5) monitoring and next steps. It is generated from fixed Stage10/11 files by `src.reporting.build_stakeholder_report`; delivery does not retune the model.

## Operating boundary

A high alert prompts an analyst to review exposures, liquidity, and hedge alternatives. It must not automatically place, size, or recommend a trade. Monitor data freshness and schema checks, alert rate, false negatives, and performance by volatility regime. Reconsider the threshold only in a pre-specified out-of-sample review.
