# Project Summary: SPY Next-Day High-Volatility Risk Alert

## The question this project addresses

A portfolio risk manager often has a short window between the U.S. market close and the following market open to decide whether the team should take a closer look at exposures, liquidity, or possible hedges. This project asks a narrow, practical question: based only on information available when SPY closes today, is tomorrow more likely than usual to be a high-volatility day?

The project does not predict whether SPY will rise or fall. It does not decide how much to trade, recommend a hedge, or execute an order. Its intended role is much smaller and safer: identify days that deserve an additional human review. A high alert is a prompt to investigate, not an instruction to act.

## What we built

We assembled a reproducible workflow around daily SPY market data from Nasdaq. The retained source snapshot contains unadjusted daily open, high, low, close, and volume observations from September 2016 through September 2026. The raw file is kept separately from all derived data so that the project can be rerun and audited.

The workflow checks dates, types, duplicate records, price ranges, and missing values before doing any analysis. Extreme daily returns are recorded rather than deleted, because the unusual market days that look inconvenient to a statistical model can be the exact days a risk process should notice. Exploratory analysis then describes the behavior of returns, trading ranges, volume, and volatility over time.

For the baseline model, we created features that would have been known at the close: recent return magnitude, intraday range, changes in volume, rolling volatility, recent momentum, and weekday indicators. We split history in chronological order into training, validation, and later test periods. This matters because it avoids letting future information make a historical test look better than it would have in real use.

A day is labelled high-volatility when the next day’s absolute SPY return exceeds the 90th-percentile threshold calculated from training history. The model is a deliberately simple, class-balanced logistic regression. Simplicity is a feature here: the objective is an understandable benchmark and decision-support signal, not a claim of a trading advantage.

## What we found

On the future-like test period, the baseline’s PR-AUC was 0.293. PR-AUC focuses on ranking rare high-volatility days more appropriately than raw accuracy. A bootstrap check produced an uncertainty interval from 0.179 to 0.457, which is broad enough to require caution.

At the validation-selected alert cutoff of 0.52, the model captured 17 of 35 high-volatility days, or 48.6%, while creating alerts on 14.0% of sessions. This means the risk analyst would review roughly one in seven sessions, but the model would still miss just over half of the high-volatility days. Increasing the cutoff to 0.70 reduces the review workload to 5.8% of sessions, but captures only 9 of the 35 high-volatility days. The lower workload is therefore a trade-off, not an improvement.

The most important limitation appeared in the volatility-regime review. In the lower-volatility half of the test sample, recall was 0.0%. A summary metric can hide this kind of failure. For that reason, the model should not be used for automatic hedging, trading, or as the sole evidence for a risk decision.

## How the output should be used

On a normal operating day, the risk analyst would first confirm that the daily market input is current and complete. The analyst then runs the pipeline and reads the generated stakeholder report. If the score crosses the approved cutoff, the next action is not a transaction. It is a focused review of current portfolio exposures, liquidity conditions, options positions, scheduled events, and available hedge alternatives. The portfolio risk manager decides whether further analysis is warranted.

This operating sequence deliberately combines the model with judgment. A probability is useful for prioritizing attention, but it cannot know the firm’s holdings or constraints. Likewise, a low score should not end a risk discussion when another source of concern is present. The report, monitoring plan, and handoff documents are designed to make this boundary visible to both the daily user and any future maintainer.

## What should not be relied on

This project uses daily SPY data only. It does not know the portfolio’s actual positions, options exposure, liquidity needs, transaction costs, intraday market conditions, corporate actions, or broader macroeconomic context. It also relies on a historical definition of a high-volatility event; markets can change and the relationship between recent behavior and tomorrow’s volatility may weaken.

The API and saved model make the work easy to demonstrate locally, but they are not a live production deployment. The local service has no authentication, external data feed, production monitoring infrastructure, or automated scheduling. The monitoring and orchestration plans describe what would be required before a wider operational use. They do not make those controls real by themselves.

## Recommended use and next steps

The appropriate current use is a daily review trigger. After the close, an analyst can run the validated pipeline, inspect data-quality checks, read the stakeholder report, and decide whether an alert merits a discussion of exposures and hedge alternatives. A low alert should not be treated as proof that risk is absent.

Before expanding the tool’s role, the team should collect more labelled experience and monitor alert rate, false negatives, data quality, and performance by market regime. Any candidate replacement model should be tested chronologically and compared with the approved baseline before deployment. Useful future additions would include portfolio-aware risk measures, options and intraday inputs, a documented adjustment policy for corporate actions, and rolling or block-based evaluation. Threshold changes, retraining, and rollback decisions should remain human-approved and versioned.

For a new teammate, the starting point is `README.md`, followed by the stakeholder report, monitoring plan, and orchestration plan. The cumulative pipeline can be run top-to-bottom to recreate the project artifacts, while the local API is available only for controlled demonstration and integration testing.
