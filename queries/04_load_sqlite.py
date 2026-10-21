"""Flatten cached Airtable JSON into data/talentflow.db so downstream analysis is
plain SQL. Re-runnable: drops and rebuilds every table from data/raw/.

Conventions:
  - every table gets `rec_id` (the Airtable record id) as primary key
  - field names are lowercased, non-alphanumerics -> underscore
  - a link field with exactly one target is stored inline as the target rec_id
  - ALL link values are additionally written to the generic `links` table so
    many-to-many and reverse links can be checked for integrity
Supports: every finding downstream."""
import json, pathlib, re, sqlite3

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
DB = ROOT / "data" / "talentflow.db"
TABLES = ["Departments","People","Job Openings","Candidates","Applications","Interviews","Offers","Findings"]

def norm(s):
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", s.lower())).strip("_")

def main():
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE links (src_table TEXT, src_rec TEXT, field TEXT, dst_rec TEXT)")

    for t in TABLES:
        recs = json.loads((RAW / f"{t}.json").read_text())
        tname = norm(t)
        # union of all field names across all records (Airtable omits empty fields)
        cols, islink = [], {}
        for r in recs:
            for k, v in r["fields"].items():
                if k not in islink:
                    islink[k] = isinstance(v, list)
                    cols.append(k)
                islink[k] = islink[k] or isinstance(v, list)
        coldefs = ", ".join(f'"{norm(c)}"' for c in cols)
        con.execute(f'CREATE TABLE "{tname}" (rec_id TEXT PRIMARY KEY, created_time TEXT'
                    + (", " + coldefs if cols else "") + ")")
        for r in recs:
            vals = [r["id"], r.get("createdTime")]
            for c in cols:
                v = r["fields"].get(c)
                if isinstance(v, list):
                    for d in v:
                        con.execute("INSERT INTO links VALUES (?,?,?,?)", (tname, r["id"], norm(c), d))
                    # inline only when unambiguous (single target)
                    v = v[0] if len(v) == 1 else (None if not v else json.dumps(v))
                elif isinstance(v, (dict,)):
                    v = json.dumps(v)
                vals.append(v)
            con.execute(f'INSERT INTO "{tname}" VALUES ({",".join("?" * len(vals))})', vals)
        print(f"{tname:<14} {len(recs):>5} rows, {len(cols)} fields")

    con.execute("CREATE INDEX idx_links_dst ON links(dst_rec)")
    con.execute("CREATE INDEX idx_links_src ON links(src_rec, field)")
    con.commit()
    print(f"\nwrote {DB}")

if __name__ == "__main__":
    main()
