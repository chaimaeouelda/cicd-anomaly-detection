import numpy as np, pandas as pd, joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

df = pd.read_csv("data/cicd_logs.csv")

df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
for c in ["duration_s", "n_commands", "n_network_calls", "files_changed"]:
    df[c] = np.log1p(df[c])

FEATURES = ["hour_sin", "hour_cos", "duration_s", "n_commands", "n_secret_access",
            "n_network_calls", "n_ext_domains", "files_changed", "failed_steps",
            "new_ip", "commits_24h"]

X = df[FEATURES].values
y = df["label"].values

X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.3, stratify=y, random_state=42)

X_tr_normal = X_tr[y_tr == 0]
scaler = StandardScaler().fit(X_tr_normal)

np.savez("data/features.npz",
         X_train=scaler.transform(X_tr_normal),
         X_test=scaler.transform(X_te),
         y_test=y_te)
joblib.dump(scaler, "models/scaler.joblib")
joblib.dump(FEATURES, "models/features.joblib")

Xn = scaler.transform(X_tr_normal)
print("X_train (normal) :", Xn.shape)
print("X_test           :", X_te.shape, "| anomalies :", int(y_te.sum()))
print("Moyenne train    :", round(float(Xn.mean()), 4))
print("Ecart-type train :", round(float(Xn.std()), 4))
