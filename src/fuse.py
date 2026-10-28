import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, roc_curve, precision_score, recall_score, f1_score
from src.hybrid import fit_ref, hybrid_score

d = np.load("data/scores.npz")
ae_tr, ae_te = d["ae_train"], d["ae_test"]
if_tr, if_te = d["if_train"], d["if_test"]
y = d["y_test"]

ref_ae, ref_if = fit_ref(ae_tr), fit_ref(if_tr)
W = 0.5
h_tr = hybrid_score(ae_tr, if_tr, ref_ae, ref_if, W)
h_te = hybrid_score(ae_te, if_te, ref_ae, ref_if, W)

rows = [("Autoencoder", ae_tr, ae_te),
        ("IsolationForest", if_tr, if_te),
        (f"Hybride (w={W})", h_tr, h_te)]

print("=== FUSION (seuil = p95 du normal, jeu de test) ===")
for name, tr, te in rows:
    thr = np.percentile(tr, 95)
    pred = (te >= thr).astype(int)
    print(f"{name:18s} AUC={roc_auc_score(y, te):.4f}  "
          f"P={precision_score(y, pred):.3f}  R={recall_score(y, pred):.3f}  "
          f"F1={f1_score(y, pred):.3f}")
    fpr, tpr, _ = roc_curve(y, te)
    plt.plot(fpr, tpr, label=name)

plt.plot([0, 1], [0, 1], "k--")
plt.xlabel("Taux de faux positifs"); plt.ylabel("Taux de vrais positifs")
plt.title("ROC : modeles seuls vs hybride"); plt.legend()
plt.savefig("reports/roc_hybrid.png", dpi=120)
