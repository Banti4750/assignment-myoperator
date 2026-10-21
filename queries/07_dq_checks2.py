"""Phase 1 continued: follow-ups on findings from 06_dq_checks.py."""
import sqlite3, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
con = sqlite3.connect(ROOT / "data" / "talentflow.db")
con.row_factory = sqlite3.Row

def section(t):
    print("\n" + "=" * 100 + f"\n{t}\n" + "=" * 100)

section("1. Likely-duplicate-person pairs: Source, #applications, and whether sources agree")
dupe_names = [r[0] for r in con.execute("SELECT full_name FROM candidates GROUP BY 1 HAVING COUNT(*) > 1")]
total_apps_on_dupes = 0
for name in dupe_names:
    cands = con.execute(
        "SELECT rec_id, candidate_id, source, created_on, notes FROM candidates WHERE full_name=? ORDER BY created_on",
        (name,)).fetchall()
    print(f"\n  {name}:")
    for c in cands:
        napps = con.execute("SELECT COUNT(*) FROM applications WHERE candidate=?", (c["rec_id"],)).fetchone()[0]
        total_apps_on_dupes += napps
        print(f"    {c['candidate_id']:<12} source={c['source']:<12} created_on={c['created_on']}  "
              f"applications={napps}  notes={c['notes']!r}")
print(f"\n  total applications attached to these 12 candidate rows: {total_apps_on_dupes}")

section("2. Offers: Status='Pending' rows -- does decision_on being filled contradict 'pending'?")
for r in con.execute("SELECT offer_id, status, offered_on, decision_on, decline_reason FROM offers WHERE status='Pending'"):
    print(f"  {dict(r)}")

section("3. Interviews: outcome in (Cancelled, No Show) but score/recommendation/completed_on present")
for r in con.execute("""
    SELECT interview_id, outcome, round, scheduled_on, completed_on, score, recommendation
    FROM interviews WHERE outcome IN ('Cancelled','No Show') AND
    (score IS NOT NULL OR recommendation IS NOT NULL OR completed_on IS NOT NULL)
"""):
    print(f"  {dict(r)}")

section("4. How many distinct human beings are really in Candidates, if we dedup on (full_name, phone)?")
row = con.execute("SELECT COUNT(*) FROM candidates").fetchone()
distinct_pairs = con.execute("SELECT COUNT(DISTINCT full_name || '|' || phone) FROM candidates").fetchone()
print(f"  candidate rows: {row[0]}   distinct (full_name, phone) pairs: {distinct_pairs[0]}")

section("5. Candidates.Source breakdown -- base rate, for context on the VP's job-board claim")
for r in con.execute("SELECT source, COUNT(*) n FROM candidates GROUP BY 1 ORDER BY 2 DESC"):
    print(f"  {dict(r)}")
