"""Stage14 monitoring contract for the local SPY risk-alert service."""

from __future__ import annotations

MONITORING_CONTRACT = (
    {
        "layer": "Data",
        "failure_mode": "stale or missing daily market input",
        "metric": "freshness_hours",
        "threshold": "> 24 hours after the expected close",
        "owner": "risk analyst",
    },
    {
        "layer": "Data",
        "failure_mode": "schema or null-rate drift",
        "metric": "schema_match and required_feature_null_rate",
        "threshold": "schema mismatch or any required feature null rate > 0%",
        "owner": "risk analyst",
    },
    {
        "layer": "Model",
        "failure_mode": "feature or predictive-performance drift",
        "metric": "feature_PSI and rolling_PR_AUC",
        "threshold": "PSI > 0.20 or PR-AUC < 0.20 after 20 labelled events",
        "owner": "model owner",
    },
    {
        "layer": "System",
        "failure_mode": "API availability or latency degradation",
        "metric": "error_rate and p95_latency_ms",
        "threshold": "5xx/error rate > 1% or p95 > 500 ms over 1 hour",
        "owner": "platform on-call",
    },
    {
        "layer": "Business",
        "failure_mode": "unusable alert workload or missed-risk pattern",
        "metric": "20-session alert_rate and confirmed false-negative review",
        "threshold": "alert rate outside 5%-25% or any material missed-risk escalation",
        "owner": "portfolio risk manager",
    },
)


def validate_monitoring_contract(contract=MONITORING_CONTRACT) -> dict[str, int]:
    """Check that a concise contract covers every required monitoring layer."""
    required_layers = {"Data", "Model", "System", "Business"}
    present_layers = {item["layer"] for item in contract}
    required_fields = {"layer", "failure_mode", "metric", "threshold", "owner"}
    if not required_layers.issubset(present_layers):
        missing = sorted(required_layers.difference(present_layers))
        raise ValueError(f"Monitoring contract is missing layers: {missing}")
    for item in contract:
        missing = required_fields.difference(item)
        if missing or any(not str(item[field]).strip() for field in required_fields):
            raise ValueError(f"Invalid monitoring contract item: {item}")
    return {layer: sum(item["layer"] == layer for item in contract) for layer in sorted(present_layers)}
