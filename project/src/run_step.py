"""Stage15 CLI wrapper for deterministic stakeholder-report generation."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from src.reporting import build_stakeholder_report

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
LOG_PATH = PROJECT_ROOT / "logs" / "orchestration.log"


def _configure_logger() -> logging.Logger:
    """Create one file-and-console logger without duplicate handlers."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("spy_risk_alert.run_step")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        for handler in (logging.StreamHandler(), logging.FileHandler(LOG_PATH)):
            handler.setFormatter(formatter)
            logger.addHandler(handler)
    return logger


def _latest_timestamp() -> str:
    """Return the timestamp shared by the newest persisted test-metric artifact."""
    candidates = sorted(PROCESSED_DIR.glob("model_test_metrics_*.csv"))
    if not candidates:
        raise FileNotFoundError("No model_test_metrics_*.csv artifact exists")
    return candidates[-1].stem.removeprefix("model_test_metrics_")


def run_stakeholder_report(timestamp: str | None = None) -> Path:
    """Rebuild the Stage12 report from fixed Stage10/11 outputs and log the checkpoint."""
    logger = _configure_logger()
    selected_timestamp = timestamp or _latest_timestamp()
    required = {
        "test_metrics": PROCESSED_DIR / f"model_test_metrics_{selected_timestamp}.csv",
        "bootstrap": PROCESSED_DIR / f"bootstrap_pr_auc_{selected_timestamp}.csv",
        "scenarios": PROCESSED_DIR / f"evaluation_scenarios_{selected_timestamp}.csv",
        "subgroups": PROCESSED_DIR / f"evaluation_subgroups_{selected_timestamp}.csv",
        "chart": REPORTS_DIR / f"spy_evaluation_{selected_timestamp}.png",
    }
    missing = [name for name, path in required.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing report dependencies: {missing}")
    logger.info("stage=stakeholder_report start timestamp=%s", selected_timestamp)
    output = build_stakeholder_report(
        required["test_metrics"],
        required["bootstrap"],
        required["scenarios"],
        required["subgroups"],
        required["chart"].name,
        REPORTS_DIR / "spy_risk_alert_stakeholder_report.md",
    )
    logger.info("stage=stakeholder_report checkpoint=%s", output)
    return output


def main(argv: list[str] | None = None) -> None:
    """Run one supported idempotent orchestration step from the command line."""
    parser = argparse.ArgumentParser(description="Run one SPY risk-alert pipeline step")
    parser.add_argument("--stage", choices=["stakeholder-report"], required=True)
    parser.add_argument("--timestamp", help="Optional persisted artifact timestamp")
    args = parser.parse_args(argv)
    output = run_stakeholder_report(args.timestamp)
    print(output)


if __name__ == "__main__":
    main()
