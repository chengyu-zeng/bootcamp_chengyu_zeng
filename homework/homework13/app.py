"""Stage13 homework Flask prediction API."""

from pathlib import Path

import joblib
import numpy as np
from flask import Flask, jsonify, request

MODEL_PATH = Path(__file__).resolve().parent / "model" / "model.pkl"
model = joblib.load(MODEL_PATH)
app = Flask(__name__)


def parse_features(values):
    """Validate exactly two finite numeric inputs for the saved regression model."""
    if not isinstance(values, list) or len(values) != 2:
        raise ValueError("features must be a list of exactly 2 numbers")
    try:
        array = np.asarray(values, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("features must contain only numbers") from exc
    if not np.isfinite(array).all():
        raise ValueError("features must contain only finite numbers")
    return array.tolist()


def error_response(message):
    return jsonify({"error": message}), 400


@app.post("/predict")
def predict_post():
    body = request.get_json(silent=True) or {}
    if "features" not in body:
        return error_response("JSON body must contain a 'features' key")
    try:
        features = parse_features(body["features"])
    except ValueError as exc:
        return error_response(str(exc))
    return jsonify({"prediction": float(model.predict([features])[0])})


@app.get("/predict/<f1>/<f2>")
def predict_get(f1, f2):
    try:
        features = parse_features([f1, f2])
    except ValueError as exc:
        return error_response(str(exc))
    return jsonify({"prediction": float(model.predict([features])[0])})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
