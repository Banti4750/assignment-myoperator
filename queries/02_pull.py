"""Pull every table once, paginated, and cache raw JSON to data/raw/<Table>.json.
Respects the documented limits: 5 req/s per base, 100 records per page.
Backs off 31s on a 429 (the lockout is 30s). Re-runnable; overwrites the cache.
Supports every finding -- this is the single source of all data used downstream."""
import json, os, pathlib, time, urllib.parse, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
TABLES = ["Departments", "People", "Job Openings", "Candidates",
          "Applications", "Interviews", "Offers", "Findings"]
MIN_INTERVAL = 0.25          # 4 req/s, under the 5 req/s cap
_last = [0.0]

def load_env():
    for line in (ROOT / ".env").read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

def get(url, tries=4):
    for attempt in range(tries):
        wait = MIN_INTERVAL - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        req = urllib.request.Request(url, headers={"Authorization": "Bearer " + os.environ["AIRTABLE_TOKEN"]})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < tries - 1:
                print("  429 -> sleeping 31s")
                time.sleep(31)
                continue
            raise

def pull(base, table):
    """Return all records for a table, following Airtable's offset pagination."""
    records, offset, pages = [], None, 0
    while True:
        params = {"pageSize": 100}
        if offset:
            params["offset"] = offset
        url = f"https://api.airtable.com/v0/{base}/{urllib.parse.quote(table)}?" + urllib.parse.urlencode(params)
        data = get(url)
        records.extend(data.get("records", []))
        pages += 1
        offset = data.get("offset")
        if not offset:
            return records, pages

if __name__ == "__main__":
    load_env()
    base = os.environ["AIRTABLE_BASE"]
    RAW.mkdir(parents=True, exist_ok=True)
    summary = {}
    for t in TABLES:
        recs, pages = pull(base, t)
        (RAW / f"{t}.json").write_text(json.dumps(recs, indent=1))
        summary[t] = {"records": len(recs), "pages": pages}
        print(f"{t:<14} {len(recs):>6} records  ({pages} page(s))")
    (RAW / "_pull_summary.json").write_text(json.dumps(summary, indent=2))
