"""Phase 1 profiling: per-column null rate / cardinality / range, duplicate-key
checks, and referential integrity across every link field.
Reads data/talentflow.db. Prints a profile table then an integrity report."""
import sqlite3, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
con = sqlite3.connect(ROOT / "data" / "talentflow.db")
con.row_factory = sqlite3.Row
TABLES = ["departments","people","job_openings","candidates","applications","interviews","offers"]
DATEISH = re.compile(r"^\d{4}-\d{2}-\d{2}")
LINK_COLS = {  # columns whose raw value is a rec_id or JSON array of rec_ids -- never dump these
    "departments": {"job_openings", "people"},
    "people": {"reqs_as_recruiter", "department", "applications_as_recruiter",
               "referrals_made", "interviews", "reqs_as_hiring_manager"},
    "job_openings": {"recruiter", "applications", "hiring_manager", "department"},
    "candidates": {"applications"},
    "applications": {"recruiter", "candidate", "opening", "interviews", "offers", "referred_by"},
    "interviews": {"application", "interviewer"},
    "offers": {"application"},
}

print("=" * 100)
print("COLUMN PROFILE")
print("=" * 100)
print(f"{'table':<14}{'column':<24}{'n':>5}{'null':>6}{'null%':>7}{'distinct':>9}  range / sample")
for t in TABLES:
    n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    cols = [r[1] for r in con.execute(f"PRAGMA table_info({t})")]
    for c in cols:
        row = con.execute(
            f'SELECT COUNT("{c}") nn, COUNT(DISTINCT "{c}") nd, MIN("{c}") mn, MAX("{c}") mx FROM {t}').fetchone()
        nulls = n - row["nn"]
        pct = f"{100*nulls/n:.1f}%" if n else "-"
        rng = ""
        if c in LINK_COLS.get(t, set()) or c == "rec_id":
            rng = "(link -> other table; see `links`)"
        elif row["nn"]:
            mn, mx = str(row["mn"]), str(row["mx"])
            if DATEISH.match(mn) or isinstance(row["mn"], (int, float)):
                rng = f"[{mn} .. {mx}]"
            elif row["nd"] <= 8:
                vals = [r[0] for r in con.execute(
                    f'SELECT DISTINCT "{c}" FROM {t} WHERE "{c}" IS NOT NULL ORDER BY 1')]
                rng = str(vals)
        print(f"{t:<14}{c:<24}{n:>5}{nulls:>6}{pct:>7}{row['nd']:>9}  {rng}")
    print()

print("=" * 100)
print("DUPLICATE KEY CHECKS  (business keys that should be unique)")
print("=" * 100)
KEYS = [("job_openings","req_id"),("candidates","candidate_id"),("candidates","email"),
        ("candidates","phone"),("candidates","full_name"),("applications","application_id"),
        ("interviews","interview_id"),("offers","offer_id"),("people","work_email")]
for t, c in KEYS:
    dup = con.execute(f'SELECT "{c}" v, COUNT(*) n FROM {t} GROUP BY 1 HAVING n > 1 ORDER BY n DESC').fetchall()
    tot = sum(r["n"] for r in dup)
    flag = "  <-- DUPLICATES" if dup else ""
    print(f"{t}.{c:<20} {len(dup)} duplicated value(s) covering {tot} rows{flag}")
    for r in dup[:6]:
        print(f"      {r['v']!r} x{r['n']}")

print()
print("=" * 100)
print("REFERENTIAL INTEGRITY  (every link target must exist)")
print("=" * 100)
# all distinct rec_ids that exist anywhere
allids = {r[0] for r in con.execute(
    "SELECT rec_id FROM departments UNION ALL SELECT rec_id FROM people UNION ALL "
    "SELECT rec_id FROM job_openings UNION ALL SELECT rec_id FROM candidates UNION ALL "
    "SELECT rec_id FROM applications UNION ALL SELECT rec_id FROM interviews UNION ALL "
    "SELECT rec_id FROM offers")}
for r in con.execute("SELECT src_table, field, COUNT(*) n, COUNT(DISTINCT dst_rec) nd FROM links GROUP BY 1,2 ORDER BY 1,2"):
    missing = [x[0] for x in con.execute(
        "SELECT DISTINCT dst_rec FROM links WHERE src_table=? AND field=?", (r["src_table"], r["field"]))
        if x[0] not in allids]
    flag = f"  <-- {len(missing)} DANGLING" if missing else "  ok"
    print(f"{r['src_table']+'.'+r['field']:<42} {r['n']:>5} links -> {r['nd']:>4} targets{flag}")

print()
print("=" * 100)
print("LINK CARDINALITY  (how many children per parent)")
print("=" * 100)
for label, sql in [
    ("offers per application",
     "SELECT n, COUNT(*) c FROM (SELECT application, COUNT(*) n FROM offers GROUP BY 1) GROUP BY 1 ORDER BY 1"),
    ("interviews per application",
     "SELECT n, COUNT(*) c FROM (SELECT application, COUNT(*) n FROM interviews GROUP BY 1) GROUP BY 1 ORDER BY 1"),
    ("applications per candidate",
     "SELECT n, COUNT(*) c FROM (SELECT candidate, COUNT(*) n FROM applications GROUP BY 1) GROUP BY 1 ORDER BY 1"),
    ("applications per opening",
     "SELECT n, COUNT(*) c FROM (SELECT opening, COUNT(*) n FROM applications GROUP BY 1) GROUP BY 1 ORDER BY 1"),
]:
    print(f"\n  {label}:")
    for r in con.execute(sql):
        print(f"      {r['n']} per parent -> {r['c']} parent(s)")
