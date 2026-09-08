"""Stage12 stakeholder-report generation helpers."""

from pathlib import Path

import pandas as pd


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _num(value: float) -> str:
    return f"{value:.3f}"


def _single_row(path: Path) -> pd.Series:
    table = pd.read_csv(path)
    if len(table) != 1:
        raise ValueError(f"Expected exactly one row in {path.name}; found {len(table)}")
    return table.iloc[0]


def build_stakeholder_report(
    test_metrics_path: Path,
    bootstrap_path: Path,
    scenarios_path: Path,
    subgroups_path: Path,
    chart_name: str,
    output_path: Path,
) -> Path:
    """Build a decision-oriented Markdown delivery from fixed Stage10/11 outputs."""
    test = _single_row(test_metrics_path)
    bootstrap = _single_row(bootstrap_path)
    scenarios = pd.read_csv(scenarios_path)
    subgroups = pd.read_csv(subgroups_path)

    selected = scenarios.loc[scenarios["scenario"] == "validation_f1_cutoff"]
    conservative = scenarios.loc[scenarios["scenario"] == "conservative_0.70"]
    lower_volatility = subgroups.loc[subgroups["regime"] == "lower_volatility"]
    if selected.empty or conservative.empty or lower_volatility.empty:
        raise ValueError("Required Stage11 sensitivity rows are missing")

    selected = selected.iloc[0]
    conservative = conservative.iloc[0]
    lower_volatility = lower_volatility.iloc[0]
    baseline_cutoff = float(test["cutoff"])
    report = f"""# SPY Next-Day High-Volatility Risk Alert
## Stakeholder Delivery - Portfolio Risk Management

### Executive summary

**Recommendation: use the baseline only as an end-of-day manual review trigger; do not automate a hedge or trade from this signal.**

- On the future-like test period, the alert captured {_pct(test["recall"])} of high-volatility days ({int(test["true_positive"])} of {int(test["true_positive"] + test["false_negative"])}), while creating alerts on {_pct(test["alert_rate"])} of sessions.
- The model has limited ranking signal (PR-AUC {_num(test["pr_auc"])}; 600-resample interval {_num(bootstrap["lower_95"])} to {_num(bootstrap["upper_95"])}), so the estimated value is uncertain.
- Reliability is uneven: recall was {_pct(lower_volatility["recall"])} in the lower-volatility half of the test sample. This is a material reason not to use the score for automatic action.

### Decision context

The portfolio risk manager receives this output after the U.S. close and before the next market open. A high alert should trigger an analyst review of exposures, liquidity, and hedge alternatives. The output is **not** an instruction to trade, a forecast of direction, or a guarantee of loss avoidance.

### Key evidence

![Bootstrap uncertainty, cutoff sensitivity, and volatility-regime recall]({chart_name})

*Figure 1. The left panel shows uncertainty around future-test PR-AUC; the middle panel shows the review-workload versus event-capture trade-off at two fixed cutoffs; the right panel exposes the lower-volatility subgroup failure. The figure uses the held-out test predictions and does not retune the model.*

| Future-like test outcome | Value | What it means |
|---|---:|---|
| PR-AUC | {_num(test["pr_auc"])} | Some ranking signal, but modest for a rare-event decision. |
| PR-AUC uncertainty | {_num(bootstrap["lower_95"])} to {_num(bootstrap["upper_95"])} | The precision of the estimate is limited by one test sample. |
| Recall | {_pct(test["recall"])} | {_pct(1 - test["recall"])} of high-volatility days were missed. |
| Alert rate | {_pct(test["alert_rate"])} | Approximate analyst review workload per trading session. |
| Precision | {_pct(test["precision"])} | Most alerts will not be high-volatility days; alerts require human context. |

### Alternate scenario: stricter alert cutoff

| Scenario | Cutoff | Recall | Alert rate | High-volatility days captured | Decision implication |
|---|---:|---:|---:|---:|---|
| Validation-selected baseline | {baseline_cutoff:.2f} | {_pct(selected["recall"])} | {_pct(selected["alert_rate"])} | {int(selected["true_positive"])} | Default manual-review threshold. |
| Conservative scenario | 0.70 | {_pct(conservative["recall"])} | {_pct(conservative["alert_rate"])} | {int(conservative["true_positive"])} | Fewer reviews, but {int(conservative["false_negative"] - selected["false_negative"])} additional high-volatility days missed. |

Moving from the baseline to the conservative cutoff reduces alert workload by {_pct(selected["alert_rate"] - conservative["alert_rate"])} of sessions, but lowers recall by {_pct(selected["recall"] - conservative["recall"])}. This is a deliberate business trade-off, not a performance improvement.

### Assumptions and risks

| Assumption / risk | Plain-language implication | Control or next step |
|---|---|---|
| Training-defined event | A high-volatility day means next-day absolute return exceeds the 90th percentile learned from training history. | Re-estimate only on an approved rolling training schedule; do not use future information. |
| Daily SPY-only inputs | The score excludes portfolio holdings, options, intraday liquidity, and transaction costs. | Treat it as a market-risk screen; add portfolio-aware inputs before any execution use. |
| Regime instability | Market relationships can change, and lower-volatility recall was {_pct(lower_volatility["recall"])} in this test. | Monitor false negatives by regime; suspend escalation if coverage deteriorates. |
| Sample uncertainty | The bootstrap interval is wide and is based on row resampling, which does not fully represent time-series dependence. | Re-test with rolling or block evaluation as more data arrive. |
| Data quality | Provider revisions or missing records can alter the score. | Validate input freshness, schema, and date coverage before publishing an alert. |

### What this means for you

1. **Run daily after close.** If the score exceeds {baseline_cutoff:.2f}, ask a risk analyst to review exposures and possible hedge scenarios before the next open.
2. **Do not automate a hedge or trade.** The baseline missed {int(test["false_negative"])} of {int(test["true_positive"] + test["false_negative"])} high-volatility days in the future-like test, including all {int(lower_volatility["true_positive"] + lower_volatility["false_negative"])} events in the lower-volatility subgroup.
3. **Monitor before expanding use.** Track alert rate, false negatives, data-quality failures, and performance by volatility regime. Revisit the threshold only after a pre-specified, out-of-sample review.

### Reproducibility and method note

The report is generated from the fixed Stage10 chronological baseline and Stage11 held-out evaluation outputs. Features use information available by the current close; the event threshold is learned from training data only. Supporting details are in [modeling policy](../docs/modeling.md), [evaluation policy](../docs/evaluation.md), and the cumulative [project pipeline](../notebooks/project_pipeline.ipynb).
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    return output_path
