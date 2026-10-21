"""Finding candidates F4-F6: the VP's offer-acceptance claim ('~72%, I need that moving').
Tries several denominator definitions to find which one reproduces ~72%,
then checks whether the 'real' rate (decided offers only) tells a different story."""
import sqlite3, pathlib
con = sqlite3.connect(pathlib.Path(__file__).resolve().parent.parent / "data" / "talentflow.db")
con.row_factory = sqlite3.Row

def section(t): print("\n" + "=" * 100 + f"\n{t}\n" + "=" * 100)
def pct(n, d): return f"{100*n/d:.1f}%" if d else "n/a"

counts = dict(con.execute("SELECT status, COUNT(*) FROM offers GROUP BY 1").fetchall())
accepted, declined, pending = counts.get("Accepted",0), counts.get("Declined",0), counts.get("Pending",0)
total = accepted + declined + pending
print(f"Offers.Status counts: Accepted={accepted} Declined={declined} Pending={pending}  (total={total})")

section("A. Candidate definitions of 'offer acceptance rate' -- which one lands near the VP's ~72%?")
defs = [
    ("Accepted / ALL offers ever made (Pending counted against)", accepted, total),
    ("Accepted / DECIDED offers only (Pending excluded)", accepted, accepted + declined),
    ("Accepted / (Accepted + Pending)  [Declined excluded -- doesn't make sense but checking]", accepted, accepted + pending),
]
for label, n, d in defs:
    print(f"  {label:<62} {n}/{d} = {pct(n,d)}")

section("B. Sensitivity: same definitions, trailing-90-day window by Offered On (today proxy = max date in data)")
maxdate = con.execute("SELECT MAX(offered_on) FROM offers").fetchone()[0]
print(f"  last Offered On in data: {maxdate}  (using this as the data's 'today' for a trailing window)")
rows = con.execute("""
    SELECT status, COUNT(*) n FROM offers
    WHERE offered_on >= date(?, '-90 day') GROUP BY 1
""", (maxdate,)).fetchall()
d = dict((r["status"], r["n"]) for r in rows)
a90, de90, p90 = d.get("Accepted",0), d.get("Declined",0), d.get("Pending",0)
print(f"  last 90 days of Offered On: Accepted={a90} Declined={de90} Pending={p90}")
print(f"  Accepted/decided (trailing 90d): {a90}/{a90+de90} = {pct(a90, a90+de90) if a90+de90 else 'n/a (too few decided)'}")

section("C. Does the 1 offer missing Decision On, and the 4 Pending-with-a-decision-date anomaly, change this?")
anomaly = con.execute("SELECT offer_id, status, decision_on FROM offers WHERE status='Pending' AND decision_on IS NOT NULL").fetchall()
print(f"  {len(anomaly)} Pending offers carry a Decision On date (contradiction flagged in Phase 1):")
for r in anomaly: print(f"    {dict(r)}")
print(f"  If these 4 are treated as resolved (their Decision On implies a real outcome we don't have, so can't reclassify them --")
print(f"  flagging as unresolvable from this data, not guessing which way they'd go).")

section("D. Acceptance rate by source/channel -- does the channel driving the VP's job-board push also hurt acceptance?")
rows = con.execute("""
    SELECT c.source, o.status, COUNT(*) n
    FROM offers o JOIN applications a ON a.rec_id=o.application JOIN candidates c ON c.rec_id=a.candidate
    GROUP BY 1,2 ORDER BY 1,2
""").fetchall()
from collections import defaultdict
bysrc = defaultdict(dict)
for r in rows: bysrc[r["source"]][r["status"]] = r["n"]
print(f"  {'source':<14}{'accepted':>9}{'declined':>9}{'pending':>8}{'accept_rate(decided)':>22}")
for s, d in sorted(bysrc.items(), key=lambda kv: -(kv[1].get('Accepted',0)+kv[1].get('Declined',0)+kv[1].get('Pending',0))):
    a, de, p = d.get("Accepted",0), d.get("Declined",0), d.get("Pending",0)
    print(f"  {s:<14}{a:>9}{de:>9}{p:>8}{pct(a, a+de) if a+de else 'n/a':>22}")

section("E. Acceptance rate by department and by level -- any segment hiding in the average?")
rows = con.execute("""
    SELECT dp.name dept, o.status, COUNT(*) n
    FROM offers o
    JOIN applications a ON a.rec_id = o.application
    JOIN job_openings j ON j.rec_id = a.opening
    JOIN departments dp ON dp.rec_id = j.department
    GROUP BY 1, 2 ORDER BY 1, 2
""").fetchall()
bydept = defaultdict(dict)
for r in rows: bydept[r["dept"]][r["status"]] = r["n"]
print(f"  by department: {'dept':<20}{'accepted':>9}{'declined':>9}{'pending':>8}{'accept_rate':>14}")
for s, d in bydept.items():
    a, de, p = d.get("Accepted",0), d.get("Declined",0), d.get("Pending",0)
    print(f"    {s:<18}{a:>9}{de:>9}{p:>8}{pct(a,a+de) if a+de else 'n/a':>14}")

rows = con.execute("""
    SELECT j.level, o.status, COUNT(*) n
    FROM offers o JOIN applications a ON a.rec_id=o.application JOIN job_openings j ON j.rec_id=a.opening
    GROUP BY 1,2 ORDER BY 1,2
""").fetchall()
bylvl = defaultdict(dict)
for r in rows: bylvl[r["level"]][r["status"]] = r["n"]
print(f"\n  by level: {'level':<12}{'accepted':>9}{'declined':>9}{'pending':>8}{'accept_rate':>14}")
for s, d in bylvl.items():
    a, de, p = d.get("Accepted",0), d.get("Declined",0), d.get("Pending",0)
    print(f"    {s:<10}{a:>9}{de:>9}{p:>8}{pct(a,a+de) if a+de else 'n/a':>14}")

section("F. Decline reasons -- what's actually driving the 5 declines we have")
for r in con.execute("SELECT decline_reason, COUNT(*) n FROM offers WHERE status='Declined' GROUP BY 1"):
    print(f"  {dict(r)}")
