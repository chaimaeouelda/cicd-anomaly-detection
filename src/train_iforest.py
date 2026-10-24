import numpy as np, joblib
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score

d = np.load("data/features.npz")
Xtr, Xte, y = d["X_train"], d["X_test"], d["y_test"]

iso = IsolationForest(n_estimators=200, max_samples="auto",
                      contamination="auto", random_state=42, n_jobs=-1)
iso.fit(Xtr)

# score eleve = plus anormal
s_tr = -iso.score_samples(Xtr)
s_te = -iso.score_samples(Xte)
thr = float(np.percentile(s_tr, 95))
pred = (s_te > thr).astype(int)

joblib.dump(iso, "models/iforest.joblib")
joblib.dump(thr, "models/if_threshold.joblib")

print("Score moyen - normal  :", round(float(s_te[y == 0].mean()), 4))
print("Score moyen - anomalie:", round(float(s_te[y == 1].mean()), 4))
print("Seuil (p95)           :", round(thr, 4))
print("AUC       :", round(roc_auc_score(y, s_te), 4))
print("Precision :", round(precision_score(y, pred), 4))
print("Rappel    :", round(recall_score(y, pred), 4))
print("F1        :", round(f1_score(y, pred), 4))
