"""Phase 0: shape only -- field union, python type, fill count, and min/max for
date-looking and numeric fields. Deliberately NOT analysis: no rates, no joins."""
import json, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}")
TABLES = ["Departments","People","Job Openings","Candidates","Applications","Interviews","Offers","Findings"]

for t in TABLES:
    recs = json.loads((RAW / f"{t}.json").read_text())
    n = len(recs)
    print(f"\n=== {t}  ({n} records) ===")
    if not n: 
        print("  (empty table)")
        continue
    fields = {}
    for r in recs:
        for k, v in r["fields"].items():
            fields.setdefault(k, []).append(v)
    for k in sorted(fields):
        vals = fields[k]
        present = len(vals)
        miss = n - present
        ty = type(vals[0]).__name__
        extra = ""
        if ty == "str" and DATE.match(str(vals[0])):
            extra = f"  range[{min(vals)} .. {max(vals)}]"
        elif ty in ("int", "float"):
            extra = f"  range[{min(vals)} .. {max(vals)}]"
        elif ty == "str":
            u = sorted(set(vals))
            extra = f"  distinct={len(u)}" + (f" {u}" if len(u) <= 8 else "")
        elif ty == "list":
            extra = f"  link, lens{sorted(set(len(v) for v in vals))}"
        print(f"  {k:<22} {ty:<6} present={present:<4} missing={miss:<4}{extra}")
