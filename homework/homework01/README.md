# SPY Next-Day High-Volatility Risk Alert

**Stage:** Problem Framing & Scoping (Stage 01)

## Problem Statement

Portfolio risk managers must decide before each trading session whether current equity exposure needs extra review, hedging, or stress testing. That decision is often made with fragmented market information and without a consistent estimate of near-term risk. A missed high-volatility session can lead to losses that exceed the portfolio's risk tolerance, while too many warnings create alert fatigue and unnecessary trading costs.

This project will build a reproducible workflow that estimates the probability that SPY will experience a high-volatility event during the next trading session. A high-volatility event is provisionally defined as an absolute close-to-close return above the 90th percentile calculated from the training history. The model will use only information available by the current market close and will produce a risk probability, a high/normal flag, and a short explanation before the next market open. The output is a decision-support tool, not an automated trading recommendation. Initial success means exceeding the no-skill precision-recall baseline by at least 20% on a strictly out-of-sample time period and recalling at least 60% of high-volatility sessions while flagging no more than 20% of sessions.

## Stakeholder & User

- **Decision owner:** A portfolio risk manager who decides whether to request additional analysis, reduce exposure, add a hedge, or run a scenario review before the next session.
- **Primary user:** A risk analyst who runs the workflow after the U.S. market close, checks data quality, reviews the risk score, and prepares the daily risk note.
- **Secondary user:** A portfolio manager who consumes the summarized alert and explanation but does not operate the pipeline.
- **Timing and workflow:** Daily after the official market close and before the next market open. A high-risk flag triggers review; it does not automatically place a trade.
- **Stakeholder need:** A consistent and auditable warning process that focuses attention on unusual next-day risk without generating excessive alerts.

## Useful Answer & Decision

- **Answer type:** Primarily predictive, supported by descriptive diagnostics. The project will not make a causal claim about why volatility occurs.
- **Target:** Whether the next session's absolute SPY close-to-close return exceeds a high-volatility threshold estimated using past training data only.
- **Primary metric:** Precision-recall area under the curve (PR-AUC), because high-volatility sessions are expected to be a minority class.
- **Decision metrics:** Recall for high-volatility sessions, alert rate, precision, and probability calibration. ROC-AUC will be reported as a secondary metric.
- **Decision rule:** A provisional probability threshold will be selected on validation data to recall at least 60% of high-volatility sessions while keeping the alert rate at or below 20%. The threshold will be reviewed with the stakeholder rather than treated as fixed.
- **Artifacts:** An executable analysis notebook, reusable Python modules, versioned input and processed data, a scored daily risk table, diagnostic charts, and a stakeholder-ready memo or slide deck.

## Assumptions & Constraints

- Daily adjusted SPY open, high, low, close, and volume data are available from a permitted public source or API.
- End-of-day information is sufficient for an initial next-session warning; intraday order-book and options data are outside the first scope.
- Every feature and threshold must be computable using information available at prediction time. Time-based splits will be used to reduce look-ahead leakage.
- Adjusted prices, exchange calendars, missing sessions, and time zones must be handled consistently.
- API availability, rate limits, schema changes, and historical revisions may affect reproducibility; raw snapshots and source metadata will be retained.
- The analysis will run locally in a documented Python environment and should complete on a standard laptop.
- The first version covers SPY only. Results should not be assumed to generalize to individual equities or other asset classes.
- The tool is educational decision support. It does not account for portfolio holdings, transaction costs, liquidity, taxes, or the suitability of a specific hedge.
- The event definition and performance targets are provisional assumptions to be validated during EDA and modeling.

## Known Unknowns / Risks

- **Regime instability:** Relationships observed in calm markets may fail during crises. Use chronological train/validation/test splits and report performance by market regime.
- **Rare-event uncertainty:** A limited number of high-volatility days can make metrics unstable. Report event counts, confidence intervals where practical, and simple baselines.
- **Threshold sensitivity:** Results may change when the event percentile or alert threshold changes. Run sensitivity checks across reasonable alternatives.
- **Data leakage:** Rolling statistics or adjusted data can accidentally use future information. Shift targets explicitly and test feature timestamps.
- **Data quality:** Missing rows, duplicate dates, corporate-action adjustments, and inconsistent calendars may distort returns. Add schema and range validation before modeling.
- **Model calibration:** A model can rank risk correctly but produce unreliable probabilities. Compare predicted probabilities with observed event frequencies.
- **Action value:** Statistical lift may not translate into a useful portfolio decision. Track both model metrics and the operational alert rate, and ask the stakeholder to assess false-positive and false-negative costs.
- **No causal interpretation:** Predictive relationships will not be described as causes of volatility.

## Lifecycle Mapping

Goal -> Stage -> Deliverable

- Define the decision, user, target, success criteria, assumptions, and risks -> Problem Framing & Scoping (Stage 01) -> Scoping README and stakeholder context memo
- Establish a reproducible environment and project scaffold -> Tooling Setup (Stage 02) -> Environment specification, configuration helper, and tracked folder structure
- Demonstrate reusable Python data handling -> Python Fundamentals (Stage 03) -> Summary notebook, saved statistics, and utility function
- Acquire reproducible market and context data -> Data Acquisition & Ingestion (Stage 04) -> Validated SPY API extract, permitted public table extract, and source documentation
- Preserve raw inputs and reliable derived data -> Data Storage (Stage 05) -> Versioned raw/processed datasets and storage conventions
- Create an analysis-ready time series -> Data Preprocessing (Stage 06) -> Cleaned dataset, validation report, and reusable preprocessing functions
- Test sensitivity to extreme observations and assumptions -> Outliers & Risk Assumptions (Stage 07) -> Outlier analysis and documented treatment choices
- Understand distributions, time behavior, and relationships -> Exploratory Data Analysis (Stage 08) -> EDA notebook, reusable summary helper, and top findings
- Build leakage-safe predictors -> Feature Engineering (Stage 09) -> Feature notebook and reusable feature module
- Estimate and evaluate next-session risk -> Modeling & Evaluation -> Time-based baselines, candidate models, calibrated probabilities, and risk metrics
- Support the stakeholder's daily decision -> Results Reporting & Delivery -> Executable notebook, daily risk output, assumptions-and-risks section, and stakeholder-ready presentation

## Repo Plan

The Stage 01 submission uses the following structure:

```text
homework/homework01/
├── README.md
├── data/
├── docs/
│   └── stakeholder_context_memo.md
├── notebooks/
└── src/
```

- `data/` will hold only small Stage 01 planning artifacts, if needed. Later raw and processed market files will follow the course storage conventions.
- `notebooks/` will hold executable analyses and will be runnable from top to bottom.
- `src/` will hold reusable ingestion, validation, preprocessing, feature, and evaluation functions as those stages are completed.
- `docs/` holds stakeholder-facing materials and decision records.
- The repository-level `project/` directory will become the integrated project scaffold beginning in Stage 02; daily homework evidence will remain in its matching `homework/homeworkNN/` directory.
- Changes will be committed at each lifecycle milestone. Raw inputs will remain immutable, processed files will be reproducible from code, and the README and risk notes will be updated whenever assumptions or decision rules change.

## AI Assistance Disclosure

An AI assistant was used to help structure this Stage 01 draft and check it against the assignment rubric. The student is responsible for reviewing the framing, validating every assumption, revising the work to reflect their own understanding, and disclosing any additional AI-assisted work.
