import numpy as np, joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import (precision_recall_curve, roc_auc_score,
                             precision_score, recall_score, f1_score)
from src.hybrid import fit_ref, hybrid_score

d = np.load("data/scores.npz")
ae_tr, ae_te = d["ae_train"], d["ae_test"]
if_tr, if_te = d["if_train"], d["if_test"]
y = d["y_test"]
ref_ae, ref_if = fit_ref(ae_tr), fit_ref(if_tr)

iv, it = train_test_split(np.arange(len(y)), test_size=0.5, stratify=y, random_state=42)

def hyb(w, idx):
    return hybrid_score(ae_te[idx], if_te[idx], ref_ae, ref_if, w)

def best_thr(h, yy):
    p, r, t = precision_recall_curve(yy, h)
    f1 = 2 * p[:-1] * r[:-1] / np.clip(p[:-1] + r[:-1], 1e-9, None)
    k = int(np.argmax(f1))
    return float(t[k]), float(f1[k])

res = {}
for w in np.round(np.linspace(0, 1, 11), 1):
    res[float(w)] = best_thr(hyb(w, iv), y[iv])

# l'hybride doit melanger les deux modeles : w entre 0.1 et 0.9
cands = [w for w in res if 0 < w < 1]
best_w = max(cands, key=lambda w: (round(res[w][1], 4), -abs(w - 0.5)))

print("=== F1 sur validation selon w ===")
for w, (thr, f1v) in res.items():
    print(f"w={w:.1f}  seuil={thr:.3f}  F1={f1v:.3f}")

print(f"\nMeilleur w hybride : {best_w}")
print("\n=== RESULTATS SUR LE TEST FINAL ===")
for label, w in [("Autoencoder seul", 1.0), ("IsolationForest seul", 0.0),
                 (f"Hybride (w={best_w})", best_w)]:
    thr = res[w][0]
    h = hyb(w, it)
    pred = (h >= thr).astype(int)
    print(f"{label:22s} AUC={roc_auc_score(y[it], h):.4f}  "
          f"P={precision_score(y[it], pred):.3f}  "
          f"R={recall_score(y[it], pred):.3f}  F1={f1_score(y[it], pred):.3f}")

cfg = {"w": best_w, "thr": res[best_w][0], "ref_ae": ref_ae, "ref_if": ref_if}
joblib.dump(cfg, "models/hybrid_config.joblib")
print("\nConfiguration sauvegardee : models/hybrid_config.joblib")

plt.plot(list(res), [v[1] for v in res.values()], marker="o")
plt.xlabel("poids w (1 = autoencoder seul, 0 = isolation forest seule)")
plt.ylabel("F1 (validation)"); plt.title("Choix du poids w")
plt.savefig("reports/tune_w.png", dpi=120)
