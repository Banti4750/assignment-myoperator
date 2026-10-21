"""Finding candidates F1-F3: the VP's job-board claim.
'job boards bring in 26.9% of our hires' and 'biggest channel by a wide margin'.
Hire = Offers.Status='Accepted' (confirmed 1:1 with Applications.Stage='Hired' in Phase 1).
Channel = Candidates.Source (the only channel field in the data)."""
import sqlite3, pathlib
con = sqlite3.connect(pathlib.Path(__file__).resolve().parent.parent / "data" / "talentflow.db")
con.row_factory = sqlite3.Row

def section(t): print("\n" + "=" * 100 + f"\n{t}\n" + "=" * 100)

section("A. Candidate volume by source (the base rate / 'biggest channel' claim)")
rows = con.execute("SELECT source, COUNT(*) n FROM candidates GROUP BY 1 ORDER BY 2 DESC").fetchall()
tot = sum(r["n"] for r in rows)
for r in rows:
    print(f"  {r['source']:<14} {r['n']:>4}  ({100*r['n']/tot:.1f}% of {tot} candidates)")

section("B. Hires by source (numerator for the 26.9% claim) -- hire = accepted offer")
rows = con.execute("""
    SELECT c.source, COUNT(*) n
    FROM offers o
    JOIN applications a ON a.rec_id = o.application
    JOIN candidates c ON c.rec_id = a.candidate
    WHERE o.status = 'Accepted'
    GROUP BY 1 ORDER BY 2 DESC
""").fetchall()
hires_tot = sum(r["n"] for r in rows)
for r in rows:
    print(f"  {r['source']:<14} {r['n']:>4}  ({100*r['n']/hires_tot:.1f}% of {hires_tot} hires)")
print(f"\n  Does any source/total match the VP's 26.9%? Checking exact fraction x/{hires_tot}:")
for r in rows:
    print(f"    {r['source']:<14} {r['n']}/{hires_tot} = {100*r['n']/hires_tot:.2f}%")

section("C. Conversion rate: hires / candidates, by source (volume vs. pain -- where VP's framing could mislead)")
cand_by_source = {r["source"]: r["n"] for r in con.execute("SELECT source, COUNT(*) n FROM candidates GROUP BY 1")}
hire_by_source = {r["source"]: r["n"] for r in con.execute("""
    SELECT c.source, COUNT(*) n FROM offers o
    JOIN applications a ON a.rec_id = o.application
    JOIN candidates c ON c.rec_id = a.candidate
    WHERE o.status='Accepted' GROUP BY 1
""")}
print(f"  {'source':<14}{'candidates':>11}{'hires':>7}{'hire_rate':>11}")
for s in sorted(cand_by_source, key=lambda s: -cand_by_source[s]):
    nc, nh = cand_by_source[s], hire_by_source.get(s, 0)
    print(f"  {s:<14}{nc:>11}{nh:>7}{100*nh/nc:>10.1f}%")

section("D. Same, at the APPLICATION level (a candidate can have >1 application; this is the funnel denominator)")
app_by_source = {r["source"]: r["n"] for r in con.execute("""
    SELECT c.source, COUNT(*) n FROM applications a JOIN candidates c ON c.rec_id = a.candidate GROUP BY 1
""")}
print(f"  {'source':<14}{'applications':>13}{'hires':>7}{'hire_rate':>11}")
for s in sorted(app_by_source, key=lambda s: -app_by_source[s]):
    na, nh = app_by_source[s], hire_by_source.get(s, 0)
    print(f"  {s:<14}{na:>13}{nh:>7}{100*nh/na:>10.1f}%")

section("E. Sensitivity: does excluding the 6 likely-duplicate-person candidate rows change the picture?")
rows = con.execute("""
    SELECT c.source, COUNT(*) n FROM offers o
    JOIN applications a ON a.rec_id = o.application
    JOIN candidates c ON c.rec_id = a.candidate
    WHERE o.status='Accepted'
      AND c.rec_id NOT IN (
        SELECT rec_id FROM candidates WHERE full_name IN (
          SELECT full_name FROM candidates GROUP BY 1 HAVING COUNT(*) > 1))
    GROUP BY 1 ORDER BY 2 DESC
""").fetchall()
tot2 = sum(r["n"] for r in rows)
for r in rows:
    print(f"  {r['source']:<14} {r['n']:>4}  ({100*r['n']/tot2:.1f}% of {tot2} hires, dupes excluded)")
