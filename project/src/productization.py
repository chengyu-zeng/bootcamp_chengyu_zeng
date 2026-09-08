"""Stage13 model-artifact and API-input helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import joblib
import numpy as np
import pandas as pd


def save_model_artifact(
    model: Any,
    feature_columns: list[str],
    cutoff: float,
    threshold: float,
    training_end: str,
    output_path: str | Path,
) -> Path:
    """Persist a fitted probabilistic model and the metadata needed to score it."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    artifact = {
        "model": model,
        "feature_columns": list(feature_columns),
        "cutoff": float(cutoff),
        "threshold": float(threshold),
        "training_end": str(training_end),
    }
    joblib.dump(artifact, path)
    return path


def load_model_artifact(path: str | Path) -> dict[str, Any]:
    """Load and minimally validate one saved risk-alert model artifact."""
    artifact = joblib.load(Path(path))
    required = {"model", "feature_columns", "cutoff", "threshold", "training_end"}
    missing = required.difference(artifact)
    if missing:
        raise ValueError(f"Model artifact is missing fields: {sorted(missing)}")
    if not artifact["feature_columns"]:
        raise ValueError("Model artifact has no feature columns")
    return artifact


def validate_feature_mapping(
    features: Any, feature_columns: list[str]
) -> pd.DataFrame:
    """Validate named numeric API inputs in the trained model's column order."""
    if not isinstance(features, Mapping):
        raise ValueError("features must be a JSON object keyed by feature name")
    expected = set(feature_columns)
    received = set(features)
    missing = sorted(expected.difference(received))
    unexpected = sorted(received.difference(expected))
    if missing or unexpected:
        detail = []
        if missing:
            detail.append(f"missing: {missing}")
        if unexpected:
            detail.append(f"unexpected: {unexpected}")
        raise ValueError("feature keys must match the model schema (" + "; ".join(detail) + ")")
    try:
        values = np.asarray([float(features[name]) for name in feature_columns], dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("all feature values must be numeric") from exc
    if not np.isfinite(values).all():
        raise ValueError("all feature values must be finite")
    return pd.DataFrame([values], columns=feature_columns)


def score_features(artifact: Mapping[str, Any], features: Any) -> dict[str, Any]:
    """Return a decision-support risk score for a validated named feature payload."""
    row = validate_feature_mapping(features, artifact["feature_columns"])
    probability = float(artifact["model"].predict_proba(row)[0, 1])
    cutoff = float(artifact["cutoff"])
    return {
        "probability": probability,
        "alert": bool(probability >= cutoff),
        "cutoff": cutoff,
        "event_threshold": float(artifact["threshold"]),
        "training_end": artifact["training_end"],
    }
