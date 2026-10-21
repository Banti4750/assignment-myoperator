"""Phase 0: probe each table with maxRecords=3 to discover field names and types.
NOTE: Airtable omits empty fields from record JSON, so fields seen here are a
LOWER BOUND on the real column set. Full discovery happens in the Phase 1 pull.
Caches to data/raw/_probe.json."""
import json, os, pathlib, time, urllib.parse, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
TABLES = ["Departments", "People", "Job Openings", "Candidates",
          "Applications", "Interviews", "Offers", "Findings"]

def load_env():
    for line in (ROOT / ".env").read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

def get(url):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + os.environ["AIRTABLE_TOKEN"]})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

if __name__ == "__main__":
    load_env()
    base = os.environ["AIRTABLE_BASE"]
    out = {}
    for t in TABLES:
        url = f"https://api.airtable.com/v0/{base}/{urllib.parse.quote(t)}?maxRecords=3"
        try:
            out[t] = {"ok": True, "records": get(url)["records"]}
        except urllib.error.HTTPError as e:
            out[t] = {"ok": False, "error": f"{e.code} {e.reason}", "body": e.read().decode()[:300]}
        time.sleep(0.25)   # stay under 5 req/s
    (ROOT / "data" / "raw" / "_probe.json").write_text(json.dumps(out, indent=2))
    for t, v in out.items():
        if not v["ok"]:
            print(f"{t:<14} ERROR {v['error']} {v['body']}")
        else:
            recs = v["records"]
            fields = {}
            for r in recs:
                for k, val in r["fields"].items():
                    fields.setdefault(k, type(val).__name__)
            print(f"{t:<14} sample={len(recs)}  fields({len(fields)}): " +
                  ", ".join(f"{k}:{t2}" for k, t2 in fields.items()))
