import numpy as np, pandas as pd, torch, joblib
from fastapi import FastAPI
from pydantic import BaseModel, Field
from src.ae_model import AutoEncoder
from src.preprocess import to_features, FEATURES
from src.hybrid import hybrid_score

class PipelineRun(BaseModel):
    hour: int = Field(ge=0, le=23)
    duration_s: float = Field(ge=0)
    n_commands: int = Field(ge=0)
    n_secret_access: int = Field(ge=0)
    n_network_calls: int = Field(ge=0)
    n_ext_domains: int = Field(ge=0)
    files_changed: int = Field(ge=0)
    failed_steps: int = Field(ge=0)
    new_ip: int = Field(ge=0, le=1)
    commits_24h: int = Field(ge=0)

app = FastAPI(title="CI/CD Anomaly Detection", version="1.0")

scaler = joblib.load("models/scaler.joblib")
iso = joblib.load("models/iforest.joblib")
cfg = joblib.load("models/hybrid_config.joblib")
ae = AutoEncoder(len(FEATURES))
ae.load_state_dict(torch.load("models/autoencoder.pt"))
ae.eval()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(run: PipelineRun):
    df = pd.DataFrame([run.model_dump()])
    x = scaler.transform(to_features(df)).astype("float32")
    t = torch.tensor(x)
    with torch.no_grad():
        ae_s = ((ae(t) - t) ** 2).mean(dim=1).numpy()
    if_s = -iso.score_samples(x)
    score = float(hybrid_score(ae_s, if_s, cfg["ref_ae"], cfg["ref_if"], cfg["w"])[0])
    blocked = score >= cfg["thr"]
    return {
        "decision": "BLOCK" if blocked else "ALLOW",
        "score": round(score, 4),
        "threshold": round(float(cfg["thr"]), 4),
        "autoencoder_score": round(float(ae_s[0]), 4),
        "isolation_forest_score": round(float(if_s[0]), 4),
    }
