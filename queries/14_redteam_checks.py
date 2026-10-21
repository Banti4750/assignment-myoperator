"""Phase 3 support queries -- verifying the strongest counter-arguments to my
own conclusions, not just asserting them."""
import sqlite3, pathlib, datetime
con = sqlite3.connect(pathlib.Path(__file__).resolve().parent.parent / "data" / "talentflow.db")
con.row_factory = sqlite3.Row
def pct(n, d): return f"{100*n/d:.1f}%" if d else "n/a"
def section(t): print("\n" + "=" * 100 + f"\n{t}\n" + "=" * 100)

section("1. Confound check: is Job Board concentrated in specific departments (structurally harder reqs)?")
rows = con.execute("""
    SELECT dp.name, c.source, COUNT(*) n
    FROM applications a JOIN candidates c ON c.rec_id=a.candidate
    JOIN job_openings j ON j.rec_id=a.opening JOIN departments dp ON dp.rec_id=j.department
    GROUP BY 1,2
""").fetchall()
from collections import defaultdict
agg = defaultdict(lambda: defaultdict(int))
for r in rows: agg[r["name"]][r["source"]] += r["n"]
for dept, srcs in agg.items():
    tot = sum(srcs.values())
    jb = srcs.get("Job Board", 0)
    print(f"  {dept:<20} total={tot:<4} Job Board share={pct(jb,tot)}")

section("2. Confound check: is Job Board concentrated under specific recruiters (a process effect, not channel)?")
rows = con.execute("""
    SELECT p.full_name, c.source, COUNT(*) n
    FROM applications a JOIN candidates c ON c.rec_id=a.candidate JOIN people p ON p.rec_id=a.recruiter
    GROUP BY 1,2
""").fetchall()
agg = defaultdict(lambda: defaultdict(int))
for r in rows: agg[r["full_name"]][r["source"]] += r["n"]
for name, srcs in agg.items():
    tot = sum(srcs.values())
    jb = srcs.get("Job Board", 0)
    print(f"  {name:<20} total={tot:<4} Job Board share={pct(jb,tot)}")

section("3. Engagement confound: No Show / Withdrawn rate by source (ghosting vs. channel quality)")
rows = con.execute("""
    SELECT c.source,
           SUM(CASE WHEN a.rejection_reason='No Show' THEN 1 ELSE 0 END) no_show,
           SUM(CASE WHEN a.stage='Withdrawn' THEN 1 ELSE 0 END) withdrawn,
           COUNT(*) total
    FROM applications a JOIN candidates c ON c.rec_id=a.candidate GROUP BY 1
""").fetchall()
for r in rows:
    print(f"  {r['source']:<14} no_show={pct(r['no_show'],r['total'])}  withdrawn={pct(r['withdrawn'],r['total'])}  (n={r['total']})")

section("4. Offer-acceptance red-team: how stale are the 5 Pending offers? (if old, VP's framing gains support)")
maxdate = con.execute("SELECT MAX(offered_on) FROM offers").fetchone()[0]
print(f"  data's latest Offered On: {maxdate}")
for r in con.execute("SELECT offer_id, offered_on, decision_on FROM offers WHERE status='Pending'"):
    d = datetime.date.fromisoformat(maxdate) - datetime.date.fromisoformat(r["offered_on"])
    print(f"  {dict(r)}  -> {d.days} days since offered, as of the data's latest date")

section("5. Statistical margin: is 72.2% (VP's def) distinguishable from 83.9% (decided-only) at n=31/36?")
import math
def wilson_ish_se(p, n):
    return math.sqrt(p*(1-p)/n) if n else float("nan")
p1, n1 = 26/36, 36
p2, n2 = 26/31, 31
print(f"  Def A (26/36=72.2%):  SE={wilson_ish_se(p1,n1)*100:.1f} pts  ->  rough 95% CI [{(p1-1.96*wilson_ish_se(p1,n1))*100:.0f}%, {min(100,(p1+1.96*wilson_ish_se(p1,n1))*100):.0f}%]")
print(f"  Def B (26/31=83.9%):  SE={wilson_ish_se(p2,n2)*100:.1f} pts  ->  rough 95% CI [{(p2-1.96*wilson_ish_se(p2,n2))*100:.0f}%, {min(100,(p2+1.96*wilson_ish_se(p2,n2))*100):.0f}%]")
print(f"  gap between point estimates: {(p2-p1)*100:.1f} points")

section("6. Are the duplicate Application IDs a batch-import artifact? (check created_time gap)")
rows = con.execute("""
    SELECT application_id, rec_id, created_time, applied_on FROM applications
    WHERE application_id IN (SELECT application_id FROM applications GROUP BY 1 HAVING COUNT(*)>1)
    ORDER BY application_id, created_time
""").fetchall()
for r in rows:
    print(f"  {dict(r)}")

section("7. Referral self-selection: do referred candidates skew toward openings with a known hiring manager overlap?")
# crude proxy: are referred-by people (referrers) themselves People records tied to the same department as the opening?
rows = con.execute("""
    SELECT a.application_id, p_ref.full_name referrer, dp_ref.name referrer_dept, dp_open.name opening_dept
    FROM applications a
    JOIN people p_ref ON p_ref.rec_id = a.referred_by
    JOIN departments dp_ref ON dp_ref.rec_id = p_ref.department
    JOIN job_openings j ON j.rec_id = a.opening
    JOIN departments dp_open ON dp_open.rec_id = j.department
""").fetchall()
same = sum(1 for r in rows if r["referrer_dept"] == r["opening_dept"])
print(f"  {same} of {len(rows)} referrals are to the referrer's own department (informal vetting plausible)")
for r in rows:
    flag = "SAME DEPT" if r["referrer_dept"]==r["opening_dept"] else ""
    print(f"    {dict(r)} {flag}")
