import numpy as np, torch, joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score
from src.ae_model import AutoEncoder

d = np.load("data/features.npz")
Xtr = d["X_train"].astype("float32")
Xte = d["X_test"].astype("float32")
y = d["y_test"]

model = AutoEncoder(Xtr.shape[1])
model.load_state_dict(torch.load("models/autoencoder.pt"))
model.eval()

def errors(X):
    x = torch.tensor(X)
    with torch.no_grad():
        return ((model(x) - x) ** 2).mean(dim=1).numpy()

e_tr, e_te = errors(Xtr), errors(Xte)
thr = float(np.percentile(e_tr, 95))
joblib.dump(thr, "models/ae_threshold.joblib")

pred = (e_te > thr).astype(int)
print("Erreur moyenne - normal  :", round(float(e_te[y == 0].mean()), 4))
print("Erreur moyenne - anomalie:", round(float(e_te[y == 1].mean()), 4))
print("Seuil (p95)              :", round(thr, 4))
print("AUC       :", round(roc_auc_score(y, e_te), 4))
print("Precision :", round(precision_score(y, pred), 4))
print("Rappel    :", round(recall_score(y, pred), 4))
print("F1        :", round(f1_score(y, pred), 4))

plt.hist(e_te[y == 0], bins=60, alpha=.6, label="normal", density=True)
plt.hist(e_te[y == 1], bins=60, alpha=.6, label="anomalie", density=True)
plt.axvline(thr, color="k", ls="--", label="seuil")
plt.xlabel("erreur de reconstruction"); plt.legend()
plt.savefig("reports/ae_errors.png", dpi=120)
