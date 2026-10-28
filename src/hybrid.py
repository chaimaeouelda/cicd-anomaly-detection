import numpy as np

def fit_ref(train_scores):
    """Reference du trafic normal : mediane et percentile 95."""
    return {"med": float(np.median(train_scores)),
            "p95": float(np.percentile(train_scores, 95))}

def normalize(scores, ref):
    """0 = mediane du normal, 1 = p95 du normal, >1 = plus anormal que 95% du normal."""
    z = (np.asarray(scores) - ref["med"]) / (ref["p95"] - ref["med"])
    return np.clip(z, 0, 20)

def hybrid_score(ae, iff, ref_ae, ref_if, w):
    return w * normalize(ae, ref_ae) + (1 - w) * normalize(iff, ref_if)
