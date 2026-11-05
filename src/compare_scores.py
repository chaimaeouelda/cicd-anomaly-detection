import numpy as np, torch, joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, roc_curve, f1_score
from src.ae_model import AutoEncoder

d = np.load("data/features.npz")
Xtr = d["X_train"].astype("float32")
Xte = d["X_test"].astype("float32")
y = d["y_test"]

model = AutoEncoder(Xtr.shape[1])
model.load_state_dict(torch.load("models/autoencoder.pt")); model.eval()
iso = joblib.load("models/iforest.joblib")

def ae_score(X):
    x = torch.tensor(X)
    with torch.no_grad():
        return ((model(x) - x) ** 2).mean(dim=1).numpy()

ae_tr, ae_te = ae_score(Xtr), ae_score(Xte)
if_tr, if_te = -iso.score_samples(Xtr), -iso.score_samples(Xte)

np.savez("data/scores.npz", ae_train=ae_tr, ae_test=ae_te,
         if_train=if_tr, if_test=if_te, y_test=y)

print("=== COMPARAISON (jeu de test) ===")
for name, tr, te in [("Autoencoder", ae_tr, ae_te), ("IsolationForest", if_tr, if_te)]:
    thr = np.percentile(tr, 95)
    print(f"{name:16s} AUC={roc_auc_score(y, te):.4f}  F1={f1_score(y, (te > thr).astype(int)):.4f}")
print("Correlation des deux scores :", round(float(np.corrcoef(ae_te, if_te)[0, 1]), 3))

for name, te in [("Autoencoder", ae_te), ("IsolationForest", if_te)]:
    fpr, tpr, _ = roc_curve(y, te)
    plt.plot(fpr, tpr, label=name)
plt.plot([0, 1], [0, 1], "k--")
plt.xlabel("Taux de faux positifs"); plt.ylabel("Taux de vrais positifs")
plt.legend(); plt.title("Courbes ROC")
plt.savefig("reports/roc_base.png", dpi=120)
print("Scores sauvegardes : data/scores.npz")
