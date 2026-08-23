# Stakeholder Context Memo: SPY Next-Day High-Volatility Risk Alert

**To:** Portfolio Risk Manager

**From:** Student Analyst

**Decision window:** After the U.S. market close and before the next market open

**Stage:** Problem Framing & Scoping (Stage 01)

## Executive Summary

The proposed project will produce a daily estimate of the probability that SPY experiences an unusually large absolute return during the next trading session. Its purpose is to help the risk team decide when an additional review, stress test, exposure discussion, or hedge analysis is warranted. The output will be a concise risk probability and high/normal flag supported by data-quality checks and a short explanation. It will not place trades or claim to forecast return direction.

The initial event definition is a next-session absolute close-to-close return above the 90th percentile of the training history. This definition makes the warning measurable while keeping the focus on unusually volatile sessions. It is provisional: later analysis will test whether the threshold is stable and useful to the stakeholder.

## Stakeholder Decision

The portfolio risk manager owns the decision. The daily question is:

> Does the available information justify an additional portfolio-risk review before the next trading session?

A high-risk flag should prompt review, not an automatic trade. Possible responses include requesting a scenario analysis, checking concentration and liquidity, discussing exposure limits, or evaluating a hedge. A normal flag means the workflow found no elevated warning under the current model; it does not guarantee a calm session.

## User and Workflow

The primary operator is a risk analyst. After the market closes, the analyst will:

1. Refresh the approved market data.
2. Confirm that required fields, dates, and numeric ranges pass validation.
3. Run the scoring workflow using information available at that time only.
4. Review the probability, alert status, recent drivers, and known limitations.
5. Escalate a high-risk result to the risk manager before the next market open.

The portfolio manager is a secondary user who receives the summarized result. The full technical output remains available for audit and follow-up.

## Proposed Output

- A probability of a next-session high-volatility event.
- A high/normal alert based on a validation-selected threshold.
- The recent market observations or features most relevant to the score, described without causal language.
- A data-quality status and timestamp.
- A compact chart showing recent risk scores, realized events, and alert history.
- An assumptions-and-risks note linked to the model version.

## Initial Acceptance Criteria

The first version will be considered analytically promising if it:

- Uses a chronological out-of-sample evaluation with no known look-ahead leakage.
- Improves PR-AUC by at least 20% relative to the no-skill event-rate baseline.
- Recalls at least 60% of high-volatility sessions while flagging no more than 20% of sessions at the chosen validation threshold.
- Reports precision, recall, alert rate, calibration, sample size, and performance by time period.
- Produces the same result from a documented environment and saved raw-data snapshot.

These targets are provisional. The risk manager may prefer a different balance between missed events and false alarms after reviewing the first validation results.

## Key Assumptions and Risks

- Daily SPY data are a useful first proxy for broad U.S. equity-market risk.
- End-of-day data arrive in time for the intended decision window.
- A model learned from historical regimes may degrade during a new crisis or structural change.
- High-volatility events are uncommon, so results may be sensitive to a small number of observations.
- Adjusted-price revisions, missing sessions, API changes, or incorrect time alignment can change results.
- A predictive association does not establish a cause of volatility.
- Model accuracy alone does not establish economic value; false alarms consume analyst time and may lead to unnecessary trading costs.
- The project does not incorporate the actual portfolio, options-implied information, intraday liquidity, transaction costs, or hedge execution.

## Questions for Stakeholder Validation

1. Is the proposed high-volatility definition aligned with the team's risk language, or should it use a fixed return or realized-volatility threshold?
2. What is more costly: missing a high-volatility session or reviewing a false alarm?
3. What maximum daily alert rate is operationally acceptable?
4. Does the decision need a probability, a simple flag, or both?
5. Which explanations are required for the risk manager to trust and act on the result?
6. Should later versions incorporate portfolio exposure, VIX data, rates, or options information?

## Lifecycle Commitment

Each later stage will leave an auditable artifact: source and validation records, immutable raw data, reproducible preprocessing, documented outlier choices, EDA findings, leakage-safe features, chronological model evaluation, and a final stakeholder presentation with assumptions and risks. Material changes to the target, threshold, or decision rule will be recorded rather than silently overwritten.
