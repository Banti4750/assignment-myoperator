# Metrics spec — Offer Acceptance Rate

## Primary metric: Offer Acceptance Rate

**Numerator**: count of `Offers` where `Status = 'Accepted'`, `Offered On` within the window.

**Denominator**: count of `Offers` where `Status IN ('Accepted', 'Declined')` AND `Offered On`
within the window. `Pending` offers are excluded from both numerator and denominator — they
have not resolved yet and are not a failure.

**The ambiguous case, handled explicitly**: an offer with `Status = 'Pending'` and `Offered On`
**30 or more days ago** is not "still deciding" — it's a data exception. Based on this quarter's
data, 100% of offers that ever got a decision resolved within 20 days (median 11; see
`queries/15_offer_lag.py`), so 30 days is a safety margin, not a guess. These offers are:
- excluded from the rate (we don't know the true outcome),
- shown on the dashboard as a separate counter: **"N offers pending resolution >30 days"**,
- never silently dropped — if that counter is nonzero, the headline rate carries a footnote:
  "computed on N of M decided offers; see exceptions."

On this dataset, that counter is currently **3** (offers stale 49, 97, and 202 days as of the
last date in the data), out of 5 total Pending offers (2 are legitimately fresh, 0–3 days old).

**Time window**: cohort-based by `Offered On` month, trailing 90 days, reported monthly. A
cohort is only reported as "final" once every offer in it is either decided or 30+ days old —
reporting a rate on a fresh, still-maturing cohort would understate it purely from censoring
(this dataset's own extract is truncated ~7 weeks before "today," so this isn't theoretical).

**Segment**: overall, plus by Department and by Level. Suppress any segment cell with denominator
< 5 as "insufficient data" rather than showing a percentage — on this dataset, every department
and level cell has 3–14 decided offers, too small to report confidently split further (e.g. by
department *and* level together).

**Exclusions**: offers with `Status='Pending'` and `Offered On` < 30 days ago (correctly excluded
as not-yet-decided, not a failure). No field currently exists for "offer rescinded by Acme" or
"candidate still deciding past normal window with an extension granted" — if either of those are
real operational states, they need their own value in `Status`, not a inferred guess from dates.

**Validation rule to add going forward**: `Status='Pending'` must never coexist with a non-null
`Decision On`. On this dataset that rule is already violated on 4 of 36 rows (11%) — this needs
a one-time backfill/reconciliation (roadmap item 1) before the metric can be trusted at all.

**Current baseline**: 26/31 = **83.9%**, computed under this spec (3 stale-Pending offers
excluded as exceptions, 2 fresh-Pending excluded as still maturing). `queries/16_metric_support.py`.
Caveat: n=31 is small; the 95% CI is roughly [71%, 97%] (`queries/14_redteam_checks.py` §5).

**Target**: `UNKNOWN`, deliberately. I'm not setting a numeric target until the metric has run
clean for one full quarter — setting a target on a number I just proved is ambiguous at this
sample size would be committing to noise.

## Guardrail metric: Base CTC position within the role's salary band

**Why this guardrail**: if someone "fixes" acceptance by just offering more money across the
board, that shows up here before it shows up in a comp budget overrun three months later.

**Definition**: `(Base CTC − Salary Band Min) / (Salary Band Max − Salary Band Min)` per offer,
where 0 = band floor, 1 = band ceiling. Reported as the median across all offers in the window
(median, not mean — see below).

**Current baseline**: median = **0.56** (reasonable — just above the midpoint). But **7 of 36
offers (19.4%) fall entirely outside their own job's stated band**, from 0.34–0.55× band minimum
to 1.73–6.12× band maximum (`queries/16_metric_support.py`). I don't know yet whether `Base CTC`,
`Level`, or `Salary Band` is the field actually wrong on those 7 — that's an open question, not
something I'm guessing at. **This guardrail isn't trustworthy as a single number until that's
resolved**, which is part of why roadmap item 1 includes a reconciliation pass.

**What must not get worse**: median position-in-band should not drift meaningfully above 0.56
quarter over quarter without a documented reason (e.g. a market comp adjustment), and the
off-band count should trend toward 0, not stay at 19%.

## Counter-metric: post-acceptance no-show-to-start rate

**Why this counter-metric**: it's possible to inflate "acceptance rate" by pressuring candidates
into saying yes who then don't actually join — accepted-on-paper, never-started-in-practice. The
primary metric would look great while this would catch the real cost.

**Current status**: `UNKNOWN` — **this is an instrumentation gap, flagged as its own finding.**
The data has `Proposed Start Date` on every offer, but no `Actual Start Date` or
`Start Confirmed` field. There's no way to tell, from this base, whether an accepted offer ever
resulted in someone actually showing up. If this isn't tracked anywhere else at Acme, it's worth
adding before leaning on acceptance rate as a headline number at all.

## Vanity metric, named and excluded

**Total number of offers made** is not used as a KPI here. More offers isn't inherently good or
bad — it can be driven by a hiring surge (healthy) or by making offers to borderline candidates
to hit a volume target (unhealthy, and would drag the acceptance rate down for reasons that have
nothing to do with acceptance behavior). It's useful as context next to the rate, never as a
target on its own.
