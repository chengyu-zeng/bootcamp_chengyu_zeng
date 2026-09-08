"""Stage11 uncertainty and sensitivity helpers."""

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score
from src.modeling import evaluate


def bootstrap_pr_auc(y, probability, n_boot=600, seed=111):
    rng = np.random.default_rng(seed)
    y = np.asarray(y)
    probability = np.asarray(probability)
    values = []
    for _ in range(n_boot):
        ix = rng.integers(0, len(y), len(y))
        values.append(average_precision_score(y[ix], probability[ix]))
    values = np.asarray(values)
    return {
        "estimate": float(average_precision_score(y, probability)),
        "lower_95": float(np.percentile(values, 2.5)),
        "upper_95": float(np.percentile(values, 97.5)),
        "samples": int(n_boot),
    }, values


def sensitivity_tables(test, probability, cutoff):
    y = test["label"].to_numpy()
    scenarios = pd.DataFrame(
        [
            {"scenario": "validation_f1_cutoff", **evaluate(y, probability, cutoff)},
            {"scenario": "conservative_0.70", **evaluate(y, probability, 0.70)},
        ]
    )
    median = test["rolling_volatility_5_t"].median()
    records = []
    for name, mask in [
        ("lower_volatility", test["rolling_volatility_5_t"] <= median),
        ("higher_volatility", test["rolling_volatility_5_t"] > median),
    ]:
        records.append(
            {
                "regime": name,
                "rows": int(mask.sum()),
                **evaluate(y[mask], np.asarray(probability)[mask], cutoff),
            }
        )
    return scenarios, pd.DataFrame(records)
