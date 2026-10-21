"""Finding candidate F17: has Job Board's share of volume/hires shifted over
time, or is the 3.0% conversion rate stable across the whole window?"""
import sqlite3, pathlib
con = sqlite3.connect(pathlib.Path(__file__).resolve().parent.parent / "data" / "talentflow.db")
con.row_factory = sqlite3.Row

rows = con.execute("""
    SELECT substr(a.applied_on,1,7) month, c.source,
           COUNT(*) applied, SUM(CASE WHEN a.stage='Hired' THEN 1 ELSE 0 END) hired
    FROM applications a JOIN candidates c ON c.rec_id = a.candidate
    WHERE c.source IN ('Job Board', 'Referral')
    GROUP BY 1, 2 ORDER BY 1, 2
""").fetchall()
from collections import defaultdict
agg = defaultdict(dict)
for r in rows:
    agg[r["month"]][r["source"]] = (r["applied"], r["hired"])
print(f"{'month':<9}{'JobBoard applied/hired':<26}{'Referral applied/hired':<26}")
for m in sorted(agg):
    jb = agg[m].get("Job Board", (0,0))
    ref = agg[m].get("Referral", (0,0))
    print(f"{m:<9}{f'{jb[0]}/{jb[1]}':<26}{f'{ref[0]}/{ref[1]}':<26}")
