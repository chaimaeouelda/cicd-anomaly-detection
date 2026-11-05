import argparse, json, sys, time, urllib.request
from collections import defaultdict


def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=10))


def wait_api(predict_url, tries=30):
    health = predict_url.rsplit("/", 1)[0] + "/health"
    for _ in range(tries):
        try:
            urllib.request.urlopen(health, timeout=3)
            return True
        except Exception:
            time.sleep(2)
    return False


def run(file, url, min_recall=0.85, max_fpr=0.10, verbose=True):
    with open(file, encoding="utf-8") as f:
        records = json.load(f)

    per = defaultdict(lambda: {"n": 0, "ok": 0})
    meta = {}
    conf = {"ALLOW": {"ALLOW": 0, "BLOCK": 0}, "BLOCK": {"ALLOW": 0, "BLOCK": 0}}
    core = {"atk": 0, "atk_blocked": 0, "norm": 0, "norm_blocked": 0}

    for r in records:
        dec = post(url, r["payload"])["decision"]
        exp, s = r["expected"], r["scenario"]
        per[s]["n"] += 1
        per[s]["ok"] += int(dec == exp)
        meta[s] = (r["group"], exp)
        conf[exp][dec] += 1
        if r["group"] == "core":
            if exp == "BLOCK":
                core["atk"] += 1
                core["atk_blocked"] += int(dec == "BLOCK")
            else:
                core["norm"] += 1
                core["norm_blocked"] += int(dec == "BLOCK")

    tp, fn = conf["BLOCK"]["BLOCK"], conf["BLOCK"]["ALLOW"]
    fp, tn = conf["ALLOW"]["BLOCK"], conf["ALLOW"]["ALLOW"]
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    core_recall = core["atk_blocked"] / max(1, core["atk"])
    core_fpr = core["norm_blocked"] / max(1, core["norm"])
    passed = core_recall >= min_recall and core_fpr <= max_fpr

    if verbose:
        print(f"{'Scenario':30s} {'Groupe':7s} {'Attendu':8s} {'Correct':>9s} {'Taux':>6s}")
        for s in sorted(per, key=lambda k: (meta[k][1], k)):
            g, e = meta[s]
            v = per[s]
            print(f"{s:30s} {g:7s} {e:8s} {v['ok']:>4d}/{v['n']:<4d} {v['ok']/v['n']:>6.0%}")
        print()
        print("Matrice de confusion (lignes = attendu, colonnes = decision)")
        print("           ALLOW  BLOCK")
        print(f"ALLOW    {tn:7d} {fp:6d}")
        print(f"BLOCK    {fn:7d} {tp:6d}")
        print()
        print(f"Global : precision={precision:.3f}  rappel={recall:.3f}  F1={f1:.3f}")
        print(f"Core   : rappel attaques={core_recall:.1%} (min {min_recall:.0%})  "
              f"faux positifs={core_fpr:.1%} (max {max_fpr:.0%})")
        print("RESULTAT E2E :", "OK" if passed else "ECHEC")

    return {"passed": passed, "precision": precision, "recall": recall, "f1": f1,
            "core_recall": core_recall, "core_fpr": core_fpr,
            "confusion": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
            "meta": {s: {"group": g, "expected": e} for s, (g, e) in meta.items()},
            "scenarios": {s: dict(v) for s, v in per.items()}}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8000/predict")
    ap.add_argument("--file", default="samples/e2e_logs.json")
    ap.add_argument("--min-recall", type=float, default=0.85)
    ap.add_argument("--max-fpr", type=float, default=0.10)
    ap.add_argument("--report", default=None)
    a = ap.parse_args()
    if not wait_api(a.url):
        print("API injoignable")
        sys.exit(2)
    out = run(a.file, a.url, a.min_recall, a.max_fpr)
    if a.report:
        with open(a.report, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
    sys.exit(0 if out["passed"] else 1)
