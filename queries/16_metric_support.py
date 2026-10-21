"""Supports metrics.md: guardrail metric baseline (Base CTC position within the
role's salary band) and the offer-acceptance-rate baseline under the proposed
spec (30-day maturation rule applied to Pending offers)."""
import sqlite3, pathlib, datetime
con = sqlite3.connect(pathlib.Path(__file__).resolve().parent.parent / "data" / "talentflow.db")
con.row_factory = sqlite3.Row

print("=== Guardrail baseline: Base CTC position within the opening's salary band ===")
rows = con.execute("""
    SELECT o.offer_id, o.base_ctc, j.salary_band_min, j.salary_band_max
    FROM offers o JOIN applications a ON a.rec_id=o.application JOIN job_openings j ON j.rec_id=a.opening
""").fetchall()
positions = []
for r in rows:
    span = r["salary_band_max"] - r["salary_band_min"]
    pos = (r["base_ctc"] - r["salary_band_min"]) / span if span else None
    if pos is not None:
        positions.append(pos)
positions.sort()
n = len(positions)
print(f"n={n} offers. position-in-band (0=min, 1=max): min={positions[0]:.2f} median={positions[n//2]:.2f} "
      f"mean={sum(positions)/n:.2f} max={positions[-1]:.2f}")
over_max = sum(1 for p in positions if p > 1.0)
print(f"offers above the stated band max: {over_max} of {n}")

print("\n=== Offer-acceptance-rate baseline under the proposed spec (30-day maturation rule) ===")
maxdate = con.execute("SELECT MAX(offered_on) FROM offers").fetchone()[0]
rows = con.execute("SELECT offer_id, status, offered_on, decision_on FROM offers").fetchall()
accepted = declined = stale_exception = fresh_pending = 0
for r in rows:
    if r["status"] == "Accepted": accepted += 1
    elif r["status"] == "Declined": declined += 1
    elif r["status"] == "Pending":
        age = (datetime.date.fromisoformat(maxdate) - datetime.date.fromisoformat(r["offered_on"])).days
        if age >= 30: stale_exception += 1
        else: fresh_pending += 1
decided = accepted + declined
print(f"Accepted={accepted} Declined={declined} -> decided={decided}")
print(f"Fresh Pending (<30d old, correctly excluded, still maturing)={fresh_pending}")
print(f"Stale Pending (>=30d old, flagged as data-quality exception, excluded from rate)={stale_exception}")
print(f"Rate = {accepted}/{decided} = {100*accepted/decided:.1f}%")
