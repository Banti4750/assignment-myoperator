# TalentFlow / Acme Corp — Q3 roadmap exercise

## How to re-run everything

Requires Python 3 (stdlib only — no pandas/duckdb installed in this environment, so everything
here is plain `sqlite3`, `urllib`, and `json`). Needs network access to Airtable and the token
in `.env` (not committed — see below).

```sh
cd queries
python 02_pull.py            # pulls all 8 tables from Airtable, caches to ../data/raw/*.json
python 04_load_sqlite.py     # flattens the cache into ../data/talentflow.db
python 05_profile.py         # Phase 1: column profile, duplicate-key checks, referential integrity
python 06_dq_checks.py       # Phase 1: date-order violations, duplicate detail
python 07_dq_checks2.py      # Phase 1: duplicate-candidate / source follow-up
python 08_claim_jobboards.py # Phase 2: the VP's job-board claim
python 09_claim_offer_accept.py  # Phase 2: the VP's offer-acceptance claim
python 10_funnel.py          # Phase 2: funnel + volume-vs-pain + headcount
python 11_segments_baserates.py  # Phase 2: selection-effect and base-rate checks
python 12_referral_crosscheck.py # Phase 2: Source vs Referred By disagreement
python 13_time_trend.py      # Phase 2: is the job-board effect recent or structural
python 14_redteam_checks.py  # Phase 3: adversarial checks against my own conclusions
python 15_offer_lag.py       # Phase 4: offer decision-lag distribution, for the metric window
python 16_metric_support.py  # Phase 4: guardrail baseline + spec-compliant acceptance rate
```

Every script reads from `../data/talentflow.db` (built once by `02_pull.py` + `04_load_sqlite.py`)
or writes to it. Nothing re-queries the Airtable API after the initial pull — that's deliberate,
per the pack's own guidance (5 req/s limit, 30s lockout on 429). Re-running `02_pull.py` refreshes
the cache from live data if Acme's base has changed since.

`.env` holds `AIRTABLE_TOKEN` and `AIRTABLE_BASE`, gitignored. If you don't have it, the base ID
and a read-only token are in `CANDIDATE_PACK_PM.md`.

## What's in each file

| File | What it is |
|---|---|
| `findings.md` | Every finding, numbered, with the exact number, denominator, query, and confidence. |
| `memo.md` | One-page summary: what I believe, why, and what I'm uncertain about. |
| `roadmap.md` | The 6 engineer-weeks: 3 building, 3 not, sequenced, with week-7 contingent plan. |
| `metrics.md` | Full spec for offer acceptance rate — numerator, denominator, edge-case handling, guardrail, counter-metric. |
| `queries/00_schema.py` | Attempted schema pull via Airtable's metadata API — returns 403 (the token has no schema scope). Kept as evidence that field names had to be inferred from records, not fetched directly. |
| `queries/01_probe.py` | First 3-record sample per table, used in the Phase 0 report. |
| `queries/02_pull.py`–`16_metric_support.py` | The actual analysis pipeline, in the order it was run. Each file's docstring says which finding(s) it supports. |
| `data/raw/*.json` | Cached API responses, one file per table, untouched. |
| `data/talentflow.db` | SQLite database built from the cache — the thing every later query actually reads. |
| `PROCESS.md` | Session process writeup (see submission step). |

## What I'd have done with more time

I'd have chased the 7 off-band `Base CTC` offers to a root cause instead of flagging them and
moving on — that finding showed up in the last hour of the session while I was building the
metrics spec, and I didn't have time to find out whether it's a `Level`, `Salary Band`, or
`Base CTC` data-entry problem before this needed to ship.
