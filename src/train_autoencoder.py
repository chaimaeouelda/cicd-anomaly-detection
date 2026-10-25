import numpy as np, torch, torch.nn as nn
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.ae_model import AutoEncoder

torch.manual_seed(42)
X = np.load("data/features.npz")["X_train"].astype("float32")

idx = np.random.default_rng(42).permutation(len(X))
n_val = int(0.1 * len(X))
val = torch.tensor(X[idx[:n_val]])
tr = torch.tensor(X[idx[n_val:]])

model = AutoEncoder(X.shape[1])
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
loss_fn = nn.MSELoss()

best, wait, PATIENCE, EPOCHS, BS = 1e9, 0, 10, 100, 64
hist_tr, hist_val = [], []

for ep in range(1, EPOCHS + 1):
    model.train()
    perm = torch.randperm(len(tr))
    total = 0.0
    for i in range(0, len(tr), BS):
        b = tr[perm[i:i + BS]]
        opt.zero_grad()
        loss = loss_fn(model(b), b)
        loss.backward()
        opt.step()
        total += loss.item() * len(b)
    model.eval()
    with torch.no_grad():
        v = loss_fn(model(val), val).item()
    hist_tr.append(total / len(tr)); hist_val.append(v)
    if ep % 10 == 0 or ep == 1:
        print(f"Epoch {ep:3d} | train {hist_tr[-1]:.4f} | val {v:.4f}")
    if v < best:
        best, wait = v, 0
        torch.save(model.state_dict(), "models/autoencoder.pt")
    else:
        wait += 1
        if wait >= PATIENCE:
            print(f"Early stopping a l'epoch {ep}")
            break

plt.plot(hist_tr, label="train"); plt.plot(hist_val, label="validation")
plt.xlabel("epoch"); plt.ylabel("MSE"); plt.legend(); plt.title("Autoencoder")
plt.savefig("reports/ae_loss.png", dpi=120)
print("Meilleure loss validation :", round(best, 4))
print("Modele sauvegarde : models/autoencoder.pt")
