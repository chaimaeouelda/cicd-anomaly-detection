import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

with open("reports/04-e2e/e2e_report.json", encoding="utf-8") as f:
    r = json.load(f)

# 1. taux de bonne decision par scenario
names = sorted(r["scenarios"], key=lambda s: (r["meta"][s]["expected"], s))
rates = [r["scenarios"][s]["ok"] / r["scenarios"][s]["n"] * 100 for s in names]
colors = ["#2563eb" if r["meta"][s]["group"] == "core" else "#f59e0b" for s in names]
fig, ax = plt.subplots(figsize=(9, 5))
ax.barh(names, rates, color=colors)
for i, v in enumerate(rates):
    ax.text(v + 1, i, f"{v:.0f}%", va="center")
ax.set_xlim(0, 115); ax.invert_yaxis()
ax.set_xlabel("Bonne decision (%)")
ax.set_title("Test E2E par scenario (bleu = core, orange = stress)")
plt.tight_layout(); plt.savefig("reports/04-e2e/e2e_scenarios.png", dpi=120); plt.close()

# 2. matrice de confusion
c = r["confusion"]
m = [[c["tn"], c["fp"]], [c["fn"], c["tp"]]]
fig, ax = plt.subplots(figsize=(4.5, 4))
ax.imshow(m, cmap="Blues")
for i in range(2):
    for j in range(2):
        ax.text(j, i, m[i][j], ha="center", va="center", fontsize=16,
                color="white" if m[i][j] > max(max(m)) / 2 else "black")
ax.set_xticks([0, 1]); ax.set_xticklabels(["ALLOW", "BLOCK"])
ax.set_yticks([0, 1]); ax.set_yticklabels(["ALLOW", "BLOCK"])
ax.set_xlabel("Decision"); ax.set_ylabel("Attendu"); ax.set_title("Matrice de confusion E2E")
plt.tight_layout(); plt.savefig("reports/04-e2e/e2e_confusion.png", dpi=120); plt.close()
print("Graphiques : reports/04-e2e/e2e_scenarios.png, reports/04-e2e/e2e_confusion.png")
