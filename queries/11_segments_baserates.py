"""Finding candidates F11-F15: where exactly in the funnel Job Board loses people
vs Referral, whether Referral's advantage could be a selection effect (easier
roles, pre-vetted candidates), and other segment/base-rate checks."""
import sqlite3, pathlib
con = sqlite3.connect(pathlib.Path(__file__).resolve().parent.parent / "data" / "talentflow.db")
con.row_factory = sqlite3.Row

def section(t): print("\n" + "=" * 100 + f"\n{t}\n" + "=" * 100)
def pct(n, d): return f"{100*n/d:.1f}%" if d else "n/a"

section("A. Conditional conversion at each step (not cumulative) -- where does each source actually lose people?")
for src in [r[0] for r in con.execute("SELECT DISTINCT source FROM candidates ORDER BY 1")]:
    row = con.execute("""
        SELECT COUNT(*) total,
               SUM(CASE WHEN screened_on IS NOT NULL THEN 1 ELSE 0 END) screened,
               SUM(CASE WHEN first_interview_on IS NOT NULL THEN 1 ELSE 0 END) interviewed,
               SUM(CASE WHEN offered_on IS NOT NULL THEN 1 ELSE 0 END) offered,
               SUM(CASE WHEN stage='Hired' THEN 1 ELSE 0 END) hired
        FROM applications a JOIN candidates c ON c.rec_id = a.candidate WHERE c.source = ?
    """, (src,)).fetchone()
    t, s, i, o, h = row["total"], row["screened"], row["interviewed"], row["offered"], row["hired"]
    print(f"  {src:<14} applied->screened: {pct(s,t):<8} screened->interviewed: {pct(i,s) if s else 'n/a':<8} "
          f"interviewed->offered: {pct(o,i) if i else 'n/a':<8} offered->hired: {pct(h,o) if o else 'n/a':<8}")

section("B. Selection-effect check: job Level applied-to, by source (do referrals target easier roles?)")
rows = con.execute("""
    SELECT c.source, j.level, COUNT(*) n
    FROM applications a JOIN candidates c ON c.rec_id=a.candidate JOIN job_openings j ON j.rec_id=a.opening
    GROUP BY 1, 2
""").fetchall()
from collections import defaultdict
agg = defaultdict(lambda: defaultdict(int))
for r in rows: agg[r["source"]][r["level"]] += r["n"]
for src, levels in agg.items():
    tot = sum(levels.values())
    print(f"  {src:<14} " + "  ".join(f"{lvl}:{pct(n,tot)}" for lvl, n in sorted(levels.items())))

section("C. Selection-effect check: avg interview score, by source (are referred candidates just better?)")
rows = con.execute("""
    SELECT c.source, AVG(i.score) avg_score, COUNT(*) n
    FROM interviews i
    JOIN applications a ON a.rec_id = i.application
    JOIN candidates c ON c.rec_id = a.candidate
    WHERE i.outcome = 'Completed' AND i.score IS NOT NULL
    GROUP BY 1 ORDER BY 2 DESC
""").fetchall()
for r in rows:
    print(f"  {r['source']:<14} avg_score={r['avg_score']:.2f}  n_interviews={r['n']}")

section("D. Referral mechanism check: Applications.Referred By populated -- does it match Candidates.Source='Referral'?")
rows = con.execute("""
    SELECT c.source, SUM(CASE WHEN a.referred_by IS NOT NULL THEN 1 ELSE 0 END) has_referrer, COUNT(*) n
    FROM applications a JOIN candidates c ON c.rec_id = a.candidate GROUP BY 1
""").fetchall()
for r in rows:
    print(f"  source={r['source']:<14} has_referred_by={r['has_referrer']:>3} of {r['n']:>3}")

section("E. Candidate CTC gap (Expected vs Current) -- bimodal/long-tail check relevant to Comp decline reasons")
rows = con.execute("SELECT current_ctc, expected_ctc FROM candidates").fetchall()
gaps = sorted([(r["expected_ctc"] - r["current_ctc"]) / r["current_ctc"] for r in rows])
n = len(gaps)
print(f"  n={n}  min={gaps[0]:.2f} p10={gaps[n//10]:.2f} p25={gaps[n//4]:.2f} median={gaps[n//2]:.2f} "
      f"p75={gaps[3*n//4]:.2f} p90={gaps[9*n//10]:.2f} max={gaps[-1]:.2f}")
neg = sum(1 for g in gaps if g < 0)
over50 = sum(1 for g in gaps if g > 0.5)
print(f"  candidates asking for LESS than current CTC: {neg} ({pct(neg,n)})")
print(f"  candidates asking for 50%+ MORE than current CTC: {over50} ({pct(over50,n)})")

section("F. Notice period distribution (fixed buckets, not continuous -- checking for bimodality)")
for r in con.execute("SELECT notice_period_days, COUNT(*) n FROM candidates GROUP BY 1 ORDER BY 1"):
    print(f"  {r['notice_period_days']:>3} days: {r['n']:>4}  ({pct(r['n'], 300)})")

section("G. Interview recommendation -> does it predict getting an offer? (base rate check)")
rows = con.execute("""
    SELECT i.recommendation, COUNT(DISTINCT i.application) napps,
           SUM(CASE WHEN a.stage IN ('Offer','Hired') THEN 1 ELSE 0 END) got_offer
    FROM interviews i JOIN applications a ON a.rec_id = i.application
    WHERE i.recommendation IS NOT NULL AND i.round IN ('Technical 1','Technical 2','Bar Raiser','Hiring Manager')
    GROUP BY 1
""").fetchall()
# naive: count per interview row, not deduped across rounds, but ballpark base rate is fine here
for r in con.execute("""
    SELECT i.recommendation, COUNT(*) n,
           SUM(CASE WHEN a.stage IN ('Offer','Hired') THEN 1 ELSE 0 END) later_offered
    FROM interviews i JOIN applications a ON a.rec_id = i.application
    WHERE i.recommendation IS NOT NULL GROUP BY 1
"""):
    print(f"  {r['recommendation']:<16} n_interviews={r['n']:>4}  app_later_reached_offer_or_hired={pct(r['later_offered'], r['n'])}")
