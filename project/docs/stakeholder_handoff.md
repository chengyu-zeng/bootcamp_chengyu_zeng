# Stakeholder Handoff Summary

## Overview and purpose

The SPY Next-Day High-Volatility Risk Alert estimates, after the U.S. close, the probability that next-session absolute SPY close-to-close return exceeds a training-defined high-volatility threshold. It supports a portfolio risk manager's decision to request analyst review, stress testing, or hedge analysis before the next open. It does not trade, recommend a trade, or estimate causal effects.

## Key findings and recommendation

- Future-like test PR-AUC is 0.293 with a 600-resample interval of 0.179 to 0.457.
- At the validation-selected cutoff of 0.52, recall is 48.6% and alerts occur on 14.0% of sessions.
- Lower-volatility test-regime recall is 0.0%, a material reliability limitation.
- **Recommendation:** use the score only as a manual review trigger; do not automate a hedge or trade.

## Assumptions, limitations, and risks

- The high-volatility event is defined from the training-period 90th percentile; it can drift as markets change.
- Inputs are daily SPY-derived features only. Portfolio holdings, options, intraday liquidity, transaction costs, and execution constraints are excluded.
- Bootstrap row resampling quantifies sample uncertainty but does not fully capture time-series dependence.
- Provider revisions, missing records, or schema drift can change the output.

## Using the deliverables

1. From a fresh pull, install `project/requirements.txt` and run `project/notebooks/project_pipeline.ipynb` top-to-bottom. This recreates processed artifacts, the stakeholder report, and `model/spy_risk_alert_model.pkl`.
2. Read `reports/spy_risk_alert_stakeholder_report.md` before using the API; it explains the decision boundary and alternate-cutoff trade-off.
3. Start the local service with `python app.py` from `project/`, then check `GET http://127.0.0.1:5050/health`. It binds only to localhost and is not a deployed service.
4. Send a `POST http://127.0.0.1:5050/predict` JSON object containing every named feature in the saved model schema. The API returns a probability and an alert flag; an alert begins human review only.

## Suggested next steps

Monitor alert rate, false negatives, data-quality checks, and performance by volatility regime. Add portfolio-aware and market-microstructure inputs before considering any stronger operational use. Revisit the threshold only through a pre-specified out-of-sample evaluation.
