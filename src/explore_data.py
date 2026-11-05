import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)

df = pd.read_csv("data/cicd_logs.csv")
print("=== Dimensions ===")
print(df.shape[0], "lignes,", df.shape[1], "colonnes")
print("\n=== Colonnes et types ===")
print(df.dtypes)
print("\n=== Valeurs manquantes ===")
print(df.isna().sum().sum(), "au total")
print("\n=== Repartition des classes ===")
print(df["attack_type"].value_counts())
print("\n=== Apercu ===")
print(df.head(8))
print("\n=== Moyenne de chaque variable par type ===")
print(df.groupby("attack_type").mean(numeric_only=True).drop(columns=["run_id", "label"]).round(1).T)
