import numpy as np, pandas as pd

rng = np.random.default_rng(42)
N_NORMAL = 5000
N_PER_ATTACK = 100

def normal(n):
    return pd.DataFrame({
        "hour": np.clip(rng.normal(14, 3.5, n), 0, 23).astype(int),
        "duration_s": rng.lognormal(5.0, 0.4, n),
        "n_commands": rng.poisson(25, n),
        "n_secret_access": rng.poisson(1.5, n),
        "n_network_calls": rng.poisson(8, n),
        "n_ext_domains": rng.poisson(2, n),
        "files_changed": rng.poisson(6, n),
        "failed_steps": rng.poisson(0.3, n),
        "new_ip": rng.binomial(1, 0.02, n),
        "commits_24h": rng.poisson(3, n),
    })

night = [0, 1, 2, 3, 4, 23]

def secret_exfil(n):
    d = normal(n)
    d["n_secret_access"] = rng.poisson(12, n)
    d["n_ext_domains"] = rng.poisson(9, n)
    d["n_network_calls"] = rng.poisson(40, n)
    d["hour"] = rng.choice(night, n)
    d["new_ip"] = rng.binomial(1, 0.7, n)
    return d

def crypto_mining(n):
    d = normal(n)
    d["duration_s"] = rng.lognormal(7.0, 0.3, n)
    d["hour"] = rng.choice(night, n)
    d["n_network_calls"] = rng.poisson(20, n)
    return d

def malicious_commit(n):
    d = normal(n)
    d["files_changed"] = rng.poisson(40, n)
    d["n_commands"] = rng.poisson(60, n)
    d["commits_24h"] = rng.poisson(15, n)
    d["new_ip"] = rng.binomial(1, 0.8, n)
    return d

parts = []
base = normal(N_NORMAL); base["label"] = 0; base["attack_type"] = "normal"
parts.append(base)
for name, fn in [("secret_exfil", secret_exfil), ("crypto_mining", crypto_mining), ("malicious_commit", malicious_commit)]:
    d = fn(N_PER_ATTACK); d["label"] = 1; d["attack_type"] = name
    parts.append(d)

df = pd.concat(parts).sample(frac=1, random_state=42).reset_index(drop=True)
df.insert(0, "run_id", range(1, len(df) + 1))
df.to_csv("data/cicd_logs.csv", index=False)

print("Dataset genere :", df.shape)
print(df["attack_type"].value_counts())
