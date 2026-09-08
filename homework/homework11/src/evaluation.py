import numpy as np

def bootstrap_metric(y, probability, metric, n_boot=600, seed=111):
    rng=np.random.default_rng(seed); y=np.asarray(y); probability=np.asarray(probability); out=[]
    for _ in range(n_boot):
        ix=rng.integers(0,len(y),len(y)); out.append(metric(y[ix],probability[ix]))
    return np.asarray(out)
