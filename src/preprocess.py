import numpy as np

LOG_COLS = ["duration_s", "n_commands", "n_network_calls", "files_changed"]
FEATURES = ["hour_sin", "hour_cos", "duration_s", "n_commands", "n_secret_access",
            "n_network_calls", "n_ext_domains", "files_changed", "failed_steps",
            "new_ip", "commits_24h"]

def to_features(df):
    df = df.copy()
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    for c in LOG_COLS:
        df[c] = np.log1p(df[c])
    return df[FEATURES].values
