"""Finding candidate F16: Source='Referral' vs Applications.Referred By populated
are two different signals for 'this came through a referral'. Which should the
roadmap bet on? Check hire rate under the Referred-By definition instead."""
import sqlite3, pathlib
con = sqlite3.connect(pathlib.Path(__file__).resolve().parent.parent / "data" / "talentflow.db")
con.row_factory = sqlite3.Row
def pct(n, d): return f"{100*n/d:.1f}%" if d else "n/a"

print("Overlap between the two referral signals:")
row = con.execute("""
    SELECT
      SUM(CASE WHEN c.source='Referral' AND a.referred_by IS NOT NULL THEN 1 ELSE 0 END) both,
      SUM(CASE WHEN c.source='Referral' AND a.referred_by IS NULL THEN 1 ELSE 0 END) source_only,
      SUM(CASE WHEN c.source!='Referral' AND a.referred_by IS NOT NULL THEN 1 ELSE 0 END) referred_by_only,
      SUM(CASE WHEN c.source!='Referral' AND a.referred_by IS NULL THEN 1 ELSE 0 END) neither
    FROM applications a JOIN candidates c ON c.rec_id = a.candidate
""").fetchone()
print(f"  {dict(row)}")

print("\nHire rate using Referred-By-populated as the 'referral' definition instead of Source:")
row = con.execute("""
    SELECT SUM(CASE WHEN a.referred_by IS NOT NULL THEN 1 ELSE 0 END) n_referred,
           SUM(CASE WHEN a.referred_by IS NOT NULL AND a.stage='Hired' THEN 1 ELSE 0 END) hired_referred,
           SUM(CASE WHEN a.referred_by IS NULL THEN 1 ELSE 0 END) n_not,
           SUM(CASE WHEN a.referred_by IS NULL AND a.stage='Hired' THEN 1 ELSE 0 END) hired_not
    FROM applications a
""").fetchone()
print(f"  Referred By populated:     {row['hired_referred']}/{row['n_referred']} = {pct(row['hired_referred'], row['n_referred'])} hire rate")
print(f"  Referred By NOT populated: {row['hired_not']}/{row['n_not']} = {pct(row['hired_not'], row['n_not'])} hire rate")

print("\nOf the 27 applications with Referred By populated, their Candidates.Source breakdown:")
for r in con.execute("""
    SELECT c.source, COUNT(*) n FROM applications a JOIN candidates c ON c.rec_id=a.candidate
    WHERE a.referred_by IS NOT NULL GROUP BY 1 ORDER BY 2 DESC
"""):
    print(f"  {dict(r)}")
