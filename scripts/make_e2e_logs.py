import json, math, random

rng = random.Random(2026)
NIGHT = [0, 1, 2, 3, 4, 23]

def poisson(lam):
    if lam > 30:
        return max(0, round(rng.gauss(lam, math.sqrt(lam))))
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        k += 1
        p *= rng.random()
        if p <= L:
            return k - 1

def base():
    return {
        "hour": int(min(23, max(0, round(rng.gauss(14, 3.5))))),
        "duration_s": round(rng.lognormvariate(5.0, 0.4), 1),
        "n_commands": poisson(25),
        "n_secret_access": poisson(1.5),
        "n_network_calls": poisson(8),
        "n_ext_domains": poisson(2),
        "files_changed": poisson(6),
        "failed_steps": poisson(0.3),
        "new_ip": 1 if rng.random() < 0.02 else 0,
        "commits_24h": poisson(3),
    }

SCENARIOS = [
    ("normal_regular", "ALLOW", "core", 150, {}),
    ("normal_nightly_build", "ALLOW", "stress", 20, {
        "hour": lambda: rng.choice([1, 2, 3]),
        "duration_s": lambda: round(rng.lognormvariate(5.4, 0.3), 1)}),
    ("normal_release_day", "ALLOW", "stress", 20, {
        "commits_24h": lambda: poisson(8),
        "files_changed": lambda: poisson(15),
        "n_commands": lambda: poisson(40)}),
    ("attack_secret_exfil", "BLOCK", "core", 20, {
        "n_secret_access": lambda: poisson(12),
        "n_ext_domains": lambda: poisson(9),
        "n_network_calls": lambda: poisson(40),
        "hour": lambda: rng.choice(NIGHT),
        "new_ip": lambda: int(rng.random() < 0.7)}),
    ("attack_crypto_mining", "BLOCK", "core", 20, {
        "duration_s": lambda: round(rng.lognormvariate(7.0, 0.3), 1),
        "hour": lambda: rng.choice(NIGHT),
        "n_network_calls": lambda: poisson(20)}),
    ("attack_malicious_commit", "BLOCK", "core", 20, {
        "files_changed": lambda: poisson(40),
        "n_commands": lambda: poisson(60),
        "commits_24h": lambda: poisson(15),
        "new_ip": lambda: int(rng.random() < 0.8)}),
    ("attack_secret_exfil_subtle", "BLOCK", "stress", 20, {
        "n_secret_access": lambda: poisson(6),
        "n_ext_domains": lambda: poisson(5),
        "n_network_calls": lambda: poisson(20)}),
    ("attack_supply_chain_unseen", "BLOCK", "stress", 20, {
        "files_changed": lambda: poisson(25),
        "n_commands": lambda: poisson(45),
        "n_ext_domains": lambda: poisson(7),
        "new_ip": lambda: 1}),
]

records, rid = [], 1
for name, expected, group, n, over in SCENARIOS:
    for _ in range(n):
        p = base()
        for k, fn in over.items():
            p[k] = fn()
        records.append({"id": rid, "scenario": name, "expected": expected,
                        "group": group, "payload": p})
        rid += 1

rng.shuffle(records)
with open("samples/e2e_logs.json", "w", encoding="utf-8") as f:
    f.write("[\n" + ",\n".join(json.dumps(r) for r in records) + "\n]\n")
print("Logs E2E generes :", len(records))
