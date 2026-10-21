"""Phase 0: fetch base schema (tables, fields, types) via Airtable Metadata API.
One request. Caches to data/raw/_schema.json. Supports no finding directly --
it establishes the shape of the data before any analysis."""
import json, os, pathlib, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
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
    schema = get(f"https://api.airtable.com/v0/meta/bases/{base}/tables")
    out = ROOT / "data" / "raw" / "_schema.json"
    out.write_text(json.dumps(schema, indent=2))
    print(f"wrote {out} ({len(schema['tables'])} tables)")
