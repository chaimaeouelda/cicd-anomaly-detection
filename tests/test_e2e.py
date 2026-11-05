import os, sys, json, urllib.request, urllib.error
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from e2e_run import post, run, wait_api

API = os.environ.get("API_URL", "http://localhost:8000")
PREDICT = API + "/predict"


def sample(name):
    with open(os.path.join(ROOT, "samples", name), encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session", autouse=True)
def api_up():
    assert wait_api(PREDICT), "API injoignable"


def test_health():
    r = urllib.request.urlopen(API + "/health", timeout=5)
    assert json.load(r)["status"] == "ok"


def test_normal_run_is_allowed():
    assert post(PREDICT, sample("normal.json"))["decision"] == "ALLOW"


def test_suspicious_run_is_blocked():
    assert post(PREDICT, sample("suspicious.json"))["decision"] == "BLOCK"


def test_invalid_hour_is_rejected():
    bad = sample("normal.json")
    bad["hour"] = 25
    with pytest.raises(urllib.error.HTTPError) as e:
        post(PREDICT, bad)
    assert e.value.code == 422


def test_missing_field_is_rejected():
    bad = sample("normal.json")
    del bad["n_secret_access"]
    with pytest.raises(urllib.error.HTTPError) as e:
        post(PREDICT, bad)
    assert e.value.code == 422


def test_decision_is_deterministic():
    p = sample("suspicious.json")
    a, b = post(PREDICT, p), post(PREDICT, p)
    assert a["decision"] == b["decision"] and a["score"] == b["score"]


def test_e2e_core_criteria():
    out = run(os.path.join(ROOT, "samples", "e2e_logs.json"), PREDICT, verbose=False)
    assert out["passed"], out
