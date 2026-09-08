# Stage11 Evaluation and Risk Communication

Future-test PR-AUC is 0.293; the 600-resample row-bootstrap 95% interval is [0.179, 0.457]. This interval quantifies sampling uncertainty, not production reliability; row bootstrap also understates dependence risk in a time series.

The validation-selected cutoff has higher recall than a 0.70 conservative cutoff, but still misses more than half of future test events. Recall is 0.000 in the lower-volatility subgroup and 0.654 in the higher-volatility subgroup, so the global score hides a serious regime-specific failure.

**Stakeholder recommendation:** retain this only as an additional review trigger. Do not automate hedging or trading. Monitor false negatives, alert rate, data quality, and regime shifts; reassess with rolling/block evaluation before deployment.
