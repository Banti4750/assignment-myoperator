# Roadmap — 6 engineer-weeks, Q3

## Verdicts on the VP's two claims (D1)

**Claim 1 — "job boards bring in 26.9% of hires, bring the integration work forward."**
Verdict: build something different. The 26.9% is correct but misleading — Referral ties it
exactly (7/26 each), off 13 applications instead of 236. The one number that decides it:
**Job Board's interview→offer conversion is 14.4% (13/90) vs. 33–70% for every other channel.**
That's the actual problem, and more job-board integration doesn't touch it.

**Claim 2 — "offer acceptance is ~72%, I need that number moving."**
Verdict: don't build an intervention yet. The one number that decides it: **4 of 5 Pending offers
(80%) carry a decision date that contradicts their own status** — the 72% is partly measuring a
broken field, not a behavioral problem, and the "clean" 83.9% reading isn't statistically
distinguishable from 72% at this sample size either. Fix the metric before deciding there's
something to fix.

## Building (6 weeks)

### 1. Fix offer-decision instrumentation and ship the offer-acceptance metric — 1.5 weeks
**Why**: Findings #4, #5, #6, #7. You cannot tell the board a number is moving if you can't trust
the number today. This also does the one-time reconciliation of the 4 contradictory Pending
offers and the 7 off-band `Base CTC` offers found while scoping the metric.
**Unblocks**: every future conversation about offer acceptance; the metric spec in `metrics.md`.
**Sequenced first because**: it's the cheapest item, and every other acceptance-related decision
is downstream of knowing the real number.

### 2. Job Board applicant qualification step — 3 weeks
**Why**: Findings #2, #3, #9. 236 applications produced 7 hires. The conversion problem is at
interview→offer, and it's not explained by which recruiter or department handles it, and not by
candidates ghosting — it tracks with lower average interview scores. A structured pre-screen
(targeted questions at point of application, or a recruiter-facing triage score before scheduling
interviews) filters earlier instead of burning interview slots on a mismatched pool.
**Unblocks**: recruiter time currently spent on 279 screens and 90 interviews that mostly don't
convert; a cleaner read on whether job-board volume is worth its cost once filtered.
**Sequenced second because**: it's the largest, highest-volume problem, and doesn't depend on
item 1 or 3.

### 3. Instrumented referral pilot — 1.5 weeks
**Why**: Findings #8, #11. 87.5% candidate-level hire rate on referrals is real but n=8 — too
small to bet the quarter on, and likely inflated by informal vetting from the 14 staff who
currently generate referral credit. Build a clean, dedicated referral submission path (distinct
from the ambiguous `Source`/`Referred By` fields found in profiling) with visible incentive, and
fold in a one-time merge of the 6 duplicate candidate-identity pairs found in Phase 1 while
touching this part of the data model.
**Unblocks**: a real answer, next quarter, on whether referral quality survives 2–3x volume —
which is the actual question, not "does referral work" (it already clearly does at tiny scale).
**Sequenced last because**: it's a bet that needs the other two items' learnings (how big a
"normal" sample looks) to interpret correctly, and it's the smallest, most contained piece.

**Total: 1.5 + 3 + 1.5 = 6 weeks.**

## Not doing

**Deeper job-board ATS integration, as the VP literally asked for.** The data says the channel's
problem is applicant fit, not integration depth. Spending weeks on pipeline plumbing before
fixing conversion would just get more of the same low-converting volume faster. If the VP's ask
was actually about recruiter workflow efficiency rather than conversion, that's a different brief
I haven't scoped — worth asking about directly before next quarter.

**A comp/counter-offer intervention to fix acceptance.** We don't know yet if there's a real
acceptance problem — the two readings overlap statistically, and the underlying field has a
data-entry defect. Building a fix for a possibly-nonexistent problem risks solving a reporting
artifact. n=5 declines is also too few to design a targeted comp response around (3 of 5 are
Counter Offer, but that's not enough to generalize from).

**A full company-wide referral program rollout.** The 87.5% hire rate is off 8 candidates. Scaling
outreach or incentives before knowing whether quality holds at volume risks diluting the one
channel that's actually working, and burning budget on a number that might not generalize.

## Week 7, if I got it

Extend the referral pilot's instrumentation to track quality-at-scale directly (time-to-decision,
hiring-manager satisfaction, not just hire rate), and build a department/level-segmented funnel
dashboard so the next round of claims like the VP's can be checked in minutes instead of a full
session. I'd ask for this if: item 2's qualification step shows Job Board's interview→offer rate
moving meaningfully toward the 33%+ range other channels sit at, or item 3's pilot sustains a
hire rate above ~40% at 2x+ current referral volume — either result would mean there's a real
program worth building out further, not just a pilot worth watching.
