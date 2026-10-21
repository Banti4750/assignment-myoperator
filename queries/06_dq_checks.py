"""Phase 1 data-quality deep dive. Investigates the anomalies the profiler
flagged: duplicate application_id, duplicate candidate name/phone, and
date-order violations across tables. Each check prints raw rows so the
conclusion is checkable, not asserted."""
import sqlite3, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
con = sqlite3.connect(ROOT / "data" / "talentflow.db")
con.row_factory = sqlite3.Row

def section(title):
    print("\n" + "=" * 100 + f"\n{title}\n" + "=" * 100)

section("1. Duplicate application_id -- same record twice, or ID collision on different records?")
rows = con.execute("""
    SELECT application_id, rec_id, candidate, opening, stage, status, applied_on
    FROM applications
    WHERE application_id IN (
        SELECT application_id FROM applications GROUP BY application_id HAVING COUNT(*) > 1
    ) ORDER BY application_id
""").fetchall()
for r in rows:
    print(dict(r))

section("2. Duplicate candidate full_name/phone -- same person twice, or two different people sharing contact info?")
dupe_names = [r[0] for r in con.execute(
    "SELECT full_name FROM candidates GROUP BY 1 HAVING COUNT(*) > 1")]
for name in dupe_names:
    rows = con.execute(
        "SELECT rec_id, candidate_id, full_name, phone, email, city, created_on FROM candidates WHERE full_name = ?",
        (name,)).fetchall()
    print(f"\n  '{name}':")
    for r in rows:
        print(f"    {dict(r)}")

section("3. Date-order violations (should never happen if timestamps are honest)")
checks = [
    ("applications: closed_on < applied_on", """
        SELECT application_id, applied_on, closed_on FROM applications
        WHERE closed_on IS NOT NULL AND closed_on < applied_on"""),
    ("applications: screened_on < applied_on", """
        SELECT application_id, applied_on, screened_on FROM applications
        WHERE screened_on IS NOT NULL AND screened_on < applied_on"""),
    ("applications: offered_on < applied_on", """
        SELECT application_id, applied_on, offered_on FROM applications
        WHERE offered_on IS NOT NULL AND offered_on < applied_on"""),
    ("applications: closed_on < screened_on", """
        SELECT application_id, screened_on, closed_on FROM applications
        WHERE closed_on IS NOT NULL AND screened_on IS NOT NULL AND closed_on < screened_on"""),
    ("applications: final_interview_on < first_interview_on", """
        SELECT application_id, first_interview_on, final_interview_on FROM applications
        WHERE final_interview_on IS NOT NULL AND first_interview_on IS NOT NULL
          AND final_interview_on < first_interview_on"""),
    ("interviews: completed_on < scheduled_on", """
        SELECT interview_id, scheduled_on, completed_on FROM interviews
        WHERE completed_on IS NOT NULL AND completed_on < scheduled_on"""),
    ("offers: decision_on < offered_on", """
        SELECT offer_id, offered_on, decision_on FROM offers
        WHERE decision_on IS NOT NULL AND decision_on < offered_on"""),
    ("candidates: created_on after their first application's applied_on", """
        SELECT c.candidate_id, c.created_on, MIN(a.applied_on) first_app
        FROM candidates c JOIN applications a ON a.candidate = c.rec_id
        GROUP BY c.rec_id HAVING c.created_on > first_app"""),
    ("job_openings: target_close < opened_on", """
        SELECT req_id, opened_on, target_close FROM job_openings
        WHERE target_close < opened_on"""),
]
for label, sql in checks:
    rows = con.execute(sql).fetchall()
    print(f"\n  {label}: {len(rows)} violation(s)")
    for r in rows[:10]:
        print(f"      {dict(r)}")

section("4. Interview outcome vs score/recommendation/completed_on consistency")
rows = con.execute("""
    SELECT outcome, COUNT(*) n,
           SUM(CASE WHEN score IS NOT NULL THEN 1 ELSE 0 END) has_score,
           SUM(CASE WHEN recommendation IS NOT NULL THEN 1 ELSE 0 END) has_rec,
           SUM(CASE WHEN completed_on IS NOT NULL THEN 1 ELSE 0 END) has_completed
    FROM interviews GROUP BY outcome ORDER BY outcome
""").fetchall()
for r in rows:
    print(f"  {dict(r)}")

section("5. Offers status vs decision_on / decline_reason consistency")
rows = con.execute("""
    SELECT status, COUNT(*) n,
           SUM(CASE WHEN decision_on IS NOT NULL THEN 1 ELSE 0 END) has_decision,
           SUM(CASE WHEN decline_reason IS NOT NULL THEN 1 ELSE 0 END) has_decline_reason
    FROM offers GROUP BY status
""").fetchall()
for r in rows:
    print(f"  {dict(r)}")

section("6. Applications.Stage vs linked Offers.Status -- do the two 'is this a hire' signals agree?")
rows = con.execute("""
    SELECT a.stage, o.status offer_status, COUNT(*) n
    FROM applications a LEFT JOIN offers o ON o.application = a.rec_id
    GROUP BY 1, 2 ORDER BY 1, 2
""").fetchall()
for r in rows:
    print(f"  {dict(r)}")

section("7. Applications.Status ('Active'/'Closed') vs Stage -- is an 'Active' app ever in a terminal stage?")
rows = con.execute("""
    SELECT status, stage, COUNT(*) n FROM applications GROUP BY 1,2 ORDER BY 1,2
""").fetchall()
for r in rows:
    print(f"  {dict(r)}")
