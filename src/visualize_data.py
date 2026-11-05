import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("data/cicd_logs.csv")
order = ["normal", "secret_exfil", "crypto_mining", "malicious_commit"]
colors = {"normal": "#2563eb", "secret_exfil": "#dc2626",
          "crypto_mining": "#f59e0b", "malicious_commit": "#7c3aed"}

ax = df["attack_type"].value_counts().plot(kind="bar", color="#2563eb", figsize=(7, 4))
ax.set_title("Repartition des classes"); ax.set_ylabel("Nombre d'executions")
plt.xticks(rotation=20); plt.tight_layout()
plt.savefig("reports/01-dataset/data_classes.png", dpi=120); plt.close()

cols = ["duration_s", "n_secret_access", "n_network_calls", "n_ext_domains", "files_changed", "commits_24h"]
fig, axes = plt.subplots(2, 3, figsize=(13, 7))
for a, c in zip(axes.ravel(), cols):
    hi = df[c].quantile(0.99)
    for t in order:
        a.hist(df.loc[df.attack_type == t, c].clip(upper=hi), bins=30, alpha=.5,
               density=True, label=t, color=colors[t])
    a.set_title(c)
axes[0, 0].legend(fontsize=8)
plt.tight_layout(); plt.savefig("reports/01-dataset/data_distributions.png", dpi=120); plt.close()

h = df.groupby(["hour", "label"]).size().unstack(fill_value=0)
h.columns = ["normal", "attaque"]
ax = h.plot(kind="bar", stacked=True, figsize=(10, 4), color=["#2563eb", "#dc2626"])
ax.set_title("Executions par heure"); ax.set_xlabel("heure"); plt.tight_layout()
plt.savefig("reports/01-dataset/data_hours.png", dpi=120); plt.close()
print("Graphiques generes dans reports/")
