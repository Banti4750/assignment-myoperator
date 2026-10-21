"""Finding candidates F7-F10: overall funnel with denominators at each step,
and the same funnel split by source -- this is where 'volume vs pain' shows up."""
import sqlite3, pathlib
con = sqlite3.connect(pathlib.Path(__file__).resolve().parent.parent / "data" / "talentflow.db")
con.row_factory = sqlite3.Row

def section(t): print("\n" + "=" * 100 + f"\n{t}\n" + "=" * 100)
def pct(n, d): return f"{100*n/d:.1f}%" if d else "n/a"

section("A. Overall funnel (Applications, all-time, every row counted once)")
total = con.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
screened = con.execute("SELECT COUNT(*) FROM applications WHERE screened_on IS NOT NULL").fetchone()[0]
interviewed = con.execute("SELECT COUNT(*) FROM applications WHERE first_interview_on IS NOT NULL").fetchone()[0]
offered = con.execute("SELECT COUNT(*) FROM applications WHERE offered_on IS NOT NULL").fetchone()[0]
hired = con.execute("SELECT COUNT(*) FROM applications WHERE stage='Hired'").fetchone()[0]
steps = [("Applied", total, total), ("Screened", screened, total), ("First Interview", interviewed, total),
         ("Offered", offered, total), ("Hired", hired, total)]
prev = total
for name, n, d0 in steps:
    print(f"  {name:<16} {n:>4} / {d0}  ({pct(n,d0)} of all applications, {pct(n,prev)} of previous step)")
    prev = n

section("B. Where applications exit -- Stage distribution (the actual terminal states)")
for r in con.execute("SELECT stage, COUNT(*) n FROM applications GROUP BY 1 ORDER BY 2 DESC"):
    print(f"  {r['stage']:<12} {r['n']:>4}  ({pct(r['n'], total)})")

section("C. Rejection reasons, among the 218 applications with one recorded")
rr_total = con.execute("SELECT COUNT(*) FROM applications WHERE rejection_reason IS NOT NULL").fetchone()[0]
for r in con.execute("SELECT rejection_reason, COUNT(*) n FROM applications WHERE rejection_reason IS NOT NULL GROUP BY 1 ORDER BY 2 DESC"):
    print(f"  {r['rejection_reason']:<18} {r['n']:>4}  ({pct(r['n'], rr_total)} of {rr_total} with a reason)")

section("D. Funnel by source -- same steps, split out (volume-vs-pain, directly)")
for src in [r[0] for r in con.execute("SELECT DISTINCT source FROM candidates ORDER BY 1")]:
    row = con.execute("""
        SELECT COUNT(*) total,
               SUM(CASE WHEN screened_on IS NOT NULL THEN 1 ELSE 0 END) screened,
               SUM(CASE WHEN first_interview_on IS NOT NULL THEN 1 ELSE 0 END) interviewed,
               SUM(CASE WHEN offered_on IS NOT NULL THEN 1 ELSE 0 END) offered,
               SUM(CASE WHEN stage='Hired' THEN 1 ELSE 0 END) hired
        FROM applications a JOIN candidates c ON c.rec_id = a.candidate WHERE c.source = ?
    """, (src,)).fetchone()
    print(f"  {src:<14} applied={row['total']:<4} screened={row['screened']:<4}({pct(row['screened'],row['total'])})  "
          f"interviewed={row['interviewed']:<4}({pct(row['interviewed'],row['total'])})  "
          f"offered={row['offered']:<4}({pct(row['offered'],row['total'])})  "
          f"hired={row['hired']:<4}({pct(row['hired'],row['total'])})")

section("E. Time-to-fill: Opened On -> Target Close vs actual. Long tail check on days-to-hire.")
rows = con.execute("""
    SELECT a.application_id, a.applied_on, o.decision_on
    FROM applications a JOIN offers o ON o.application = a.rec_id
    WHERE o.status = 'Accepted' AND o.decision_on IS NOT NULL
""").fetchall()
import datetime
days = []
for r in rows:
    d1 = datetime.date.fromisoformat(r["applied_on"])
    d2 = datetime.date.fromisoformat(r["decision_on"])
    days.append((d2 - d1).days)
days.sort()
n = len(days)
print(f"  n={n} hires with both dates. min={days[0]} p25={days[n//4]} median={days[n//2]} p75={days[3*n//4]} max={days[-1]}")
print(f"  mean={sum(days)/n:.1f}  (compare mean vs median -- {'right-skewed/long tail' if sum(days)/n > days[n//2]+5 else 'roughly symmetric'})")
print(f"  full sorted list: {days}")

section("F. Headcount: Job Openings status vs Department budget -- any department over/under its budget?")
rows = con.execute("""
    SELECT dp.name, dp.headcount_budget, j.status, SUM(j.headcount) hc
    FROM job_openings j JOIN departments dp ON dp.rec_id = j.department
    GROUP BY 1, 2, 3 ORDER BY 1, 3
""").fetchall()
from collections import defaultdict
agg = defaultdict(lambda: defaultdict(int))
budget = {}
for r in rows:
    agg[r["name"]][r["status"]] += r["hc"]
    budget[r["name"]] = r["headcount_budget"]
for name, statuses in agg.items():
    filled = statuses.get("Filled", 0)
    print(f"  {name:<20} budget={budget[name]:<4} filled={filled:<4} statuses={dict(statuses)}")
