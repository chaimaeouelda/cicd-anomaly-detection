import json, sys, urllib.request

payload_file = sys.argv[1]
url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000/predict"

with open(payload_file, "rb") as f:
    data = f.read()
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
res = json.load(urllib.request.urlopen(req, timeout=10))
print(json.dumps(res, indent=2))

if res["decision"] == "BLOCK":
    print("PIPELINE BLOQUE : comportement anormal detecte")
    sys.exit(1)
print("Pipeline autorise")
