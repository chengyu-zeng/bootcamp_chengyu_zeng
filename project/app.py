"""Flask API for the saved SPY next-day high-volatility risk model."""

from pathlib import Path

from flask import Flask, jsonify, request

from src.productization import load_model_artifact, score_features

PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_ROOT / "model" / "spy_risk_alert_model.pkl"
MODEL_ARTIFACT = load_model_artifact(MODEL_PATH)

app = Flask(__name__)


def bad_request(message: str):
    """Return a JSON client-error response without exposing a traceback."""
    return jsonify({"error": message}), 400


@app.get("/health")
def health():
    """Show that the application loaded its model at process startup."""
    return jsonify(
        {
            "status": "ok",
            "feature_count": len(MODEL_ARTIFACT["feature_columns"]),
            "training_end": MODEL_ARTIFACT["training_end"],
        }
    )


@app.post("/predict")
def predict():
    """Score a JSON payload with exact, named model-feature values."""
    body = request.get_json(silent=True)
    if not isinstance(body, dict) or "features" not in body:
        return bad_request("JSON body must contain a 'features' object")
    try:
        result = score_features(MODEL_ARTIFACT, body["features"])
    except ValueError as exc:
        return bad_request(str(exc))
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
