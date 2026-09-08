# Stage14 Monitoring Plan

The closest production-ready component is the Stage13 localhost Flask API that scores the saved SPY next-day high-volatility model after the U.S. close. It remains decision support only: an alert starts analyst review and never executes a trade.

**Data.** A stale or missing daily batch is detected when freshness exceeds 24 hours after the expected market close; a schema mismatch or any null in a required feature is also an alert. The risk analyst receives the alert, stops scoring, and validates the provider snapshot and pipeline lineage.

**Model.** Track population-stability index (PSI) for each core feature and PR-AUC when labels arrive. PSI above 0.20, or PR-AUC below 0.20 after at least 20 labelled high-volatility events, notifies the model owner. The first runbook step is to freeze threshold changes, inspect regime and data changes, and compare against the last approved model.

**System.** Log API 5xx/error rate and one-hour p95 latency. Error rate above 1% or p95 latency above 500 ms pages platform on-call, who checks the local service, model artifact version, and dependency health; the safe fallback is the last stakeholder report plus manual review.

**Business.** The portfolio risk manager reviews the 20-session alert rate and confirmed false-negative escalations. Alert rate outside 5%-25%, or any material missed-risk event, opens a risk review ticket; the analyst documents context rather than silently retuning.

The risk analyst updates the dashboard daily; the model owner performs a monthly review. Retraining is considered every six months or after a model threshold breach, but requires portfolio risk-manager approval, chronological out-of-sample evaluation, a versioned artifact, and rollback to the prior approved model if checks fail. Issues and decisions are logged in the project change log and linked to the runbook ticket.
