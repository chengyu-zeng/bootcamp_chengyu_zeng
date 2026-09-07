"""Chronological Stage10 classification baseline for the SPY risk alert."""

from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

BASE_FEATURES = [
    "abs_return_t",
    "intraday_range_t",
    "log_volume_change_t",
    "rolling_volatility_5_t",
    "weekday_Monday",
    "weekday_Tuesday",
    "weekday_Wednesday",
    "weekday_Thursday",
    "weekday_Friday",
]
EXTRA_FEATURES = [
    "return_lag_1_t",
    "rolling_abs_return_mean_5_t",
    "rolling_return_std_10_t",
    "momentum_5_t",
]


def prepare_modeling_frame(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy(deep=True)
    result["date"] = pd.to_datetime(result["date"], errors="raise")
    result = result.sort_values("date", kind="stable").reset_index(drop=True)
    result["return_lag_1_t"] = result["return_t"].shift(1)
    result["rolling_abs_return_mean_5_t"] = result["abs_return_t"].rolling(5).mean()
    result["rolling_return_std_10_t"] = result["return_t"].rolling(10).std(ddof=1)
    result["momentum_5_t"] = result["close"].pct_change(5, fill_method=None)
    cols = ["date", *BASE_FEATURES, *EXTRA_FEATURES, "next_day_abs_return"]
    return result.loc[:, cols].dropna().reset_index(drop=True)


def evaluate(y, prob, cutoff):
    pred = (np.asarray(prob) >= cutoff).astype(int)
    return {
        "accuracy": accuracy_score(y, pred),
        "precision": precision_score(y, pred, zero_division=0),
        "recall": recall_score(y, pred, zero_division=0),
        "f1": f1_score(y, pred, zero_division=0),
        "pr_auc": average_precision_score(y, prob),
        "alert_rate": float(pred.mean()),
        "true_negative": int(confusion_matrix(y, pred, labels=[0, 1])[0, 0]),
        "false_positive": int(confusion_matrix(y, pred, labels=[0, 1])[0, 1]),
        "false_negative": int(confusion_matrix(y, pred, labels=[0, 1])[1, 0]),
        "true_positive": int(confusion_matrix(y, pred, labels=[0, 1])[1, 1]),
    }


def run_baseline(frame: pd.DataFrame) -> dict:
    data = prepare_modeling_frame(frame)
    a = int(0.6 * len(data))
    b = int(0.8 * len(data))
    train, val, test = data.iloc[:a].copy(), data.iloc[a:b].copy(), data.iloc[b:].copy()
    q = float(train.next_day_abs_return.quantile(0.9))
    for part in (train, val, test):
        part["label"] = (part.next_day_abs_return > q).astype(int)
    candidates = []
    for c in (0.3, 1.0):
        model = Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "logit",
                    LogisticRegression(
                        C=c, class_weight="balanced", max_iter=1000, random_state=42
                    ),
                ),
            ]
        )
        model.fit(train[BASE_FEATURES + EXTRA_FEATURES], train.label)
        prob = model.predict_proba(val[BASE_FEATURES + EXTRA_FEATURES])[:, 1]
        candidates.append((c, model, prob, evaluate(val.label, prob, 0.5)))
    c, model, prob, selection = max(candidates, key=lambda item: item[3]["pr_auc"])
    grid = np.linspace(0.05, 0.95, 91)
    cutoff = max(grid, key=lambda x: evaluate(val.label, prob, float(x))["f1"])
    val_metrics = evaluate(val.label, prob, float(cutoff))
    test_prob = model.predict_proba(test[BASE_FEATURES + EXTRA_FEATURES])[:, 1]
    test_metrics = evaluate(test.label, test_prob, float(cutoff))
    return {
        "data": data,
        "train": train,
        "validation": val,
        "test": test,
        "threshold": q,
        "regularization_c": c,
        "cutoff": float(cutoff),
        "validation_probability": prob,
        "test_probability": test_prob,
        "validation_metrics": val_metrics,
        "test_metrics": test_metrics,
    }
