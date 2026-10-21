"""Supports metrics.md: distribution of days from Offered On to Decision On,
among offers that actually have both dates -- informs the maturation window
for the offer-acceptance-rate metric spec."""
import sqlite3, pathlib, datetime
con = sqlite3.connect(pathlib.Path(__file__).resolve().parent.parent / "data" / "talentflow.db")
con.row_factory = sqlite3.Row

rows = con.execute("""
    SELECT offer_id, status, offered_on, decision_on FROM offers
    WHERE decision_on IS NOT NULL
""").fetchall()
lags = []
for r in rows:
    d1 = datetime.date.fromisoformat(r["offered_on"])
    d2 = datetime.date.fromisoformat(r["decision_on"])
    lags.append((d2 - d1).days)
lags.sort()
n = len(lags)
print(f"n={n} offers with both dates (includes the 4 anomalous Pending-with-decision_on rows)")
print(f"min={lags[0]} p25={lags[n//4]} median={lags[n//2]} p75={lags[3*n//4]} max={lags[-1]}")
print(f"sorted: {lags}")
print(f"\n% decided within 14 days: {100*sum(1 for l in lags if l<=14)/n:.1f}%")
print(f"% decided within 30 days: {100*sum(1 for l in lags if l<=30)/n:.1f}%")
print(f"% decided within 60 days: {100*sum(1 for l in lags if l<=60)/n:.1f}%")
