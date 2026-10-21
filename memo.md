# Memo — TalentFlow Q3 at Acme

## One paragraph

The VP's two numbers are both exactly reproducible in the data — and both are more complicated
than they sound. Job boards tie referrals for the most hires (7 of 26 each), but they're the
highest-volume *and* worst-converting channel we have, while referrals are tiny and extremely
efficient. "Bring forward job-board integration" would pour more volume into the weakest link.
Offer acceptance at "~72%" only reproduces by counting unresolved offers as rejections; the
cleaner reading is 83.9%, and at this sample size (31–36 offers) the two numbers aren't even
statistically distinguishable. I'm not funding a comp intervention for a problem I can't confirm
exists. What I am funding: fixing the measurement, fixing the Job Board funnel, and a small,
honest referral pilot.

## What the data says that Acme probably doesn't know

Job Board and Referral tie exactly at 26.9% of hires each — the VP's number is right, but reading
it as "job boards dominate" misses that Referral gets there off 13 applications while Job Board
needs 236. Job Board's conversion problem is concentrated at interview→offer (14.4%, vs. 33–70%
everywhere else), and it isn't explained by which department or recruiter handles it — the mix is
uniform across both. Separately, 4 of the 5 "Pending" offers have a decision date already logged
against them, meaning Acme's own acceptance number has been partly built on a field that
contradicts itself for 11% of all offers ever made. And while building the metric spec I found
something nobody asked about: 7 of 36 offers (19%) have a base salary outside the job's own
stated band, by up to 6x. Nobody flagged that to me — I found it checking a guardrail metric.

## What I believe, and why

`OBSERVED`: Job Board = 63.7% of candidates, 3.0% hire rate. Referral = 2.7% of candidates, 53.8%
hire rate (application-level). Offer acceptance is 72.2% if Pending counts as a loss, 83.9% if it
doesn't, and the two 95% confidence intervals overlap.

`INFERRED`: Job Board's low conversion is a pool-quality problem, not an engagement problem —
Job Board candidates don't ghost more than any other channel (5.1% no-show, in line with
everyone else), but they do interview worse on average (2.66 avg score vs. 3.19–3.38 elsewhere).
That points at pre-application screening, not post-application chasing. Referral's advantage is
`INFERRED` to be mostly selection bias: the 14 staff who get referral credit are informally
vetting before they refer, which is a mechanism that may not survive scaling to a broader program.

`ASSUMED`: that "hire" means an accepted offer (the data gives two signals — `Stage='Hired'` and
`Offers.Status='Accepted'` — and they agree on every single row, so I'm comfortable with this).
I'm also assuming the VP's "bring forward the integration work" means improving performance of
the channel, not an unrelated ops/workflow goal — if it's the latter, my D1 verdict doesn't apply
and I'd want to know that before cutting the work.

## The decision I'm making, and the bet it rests on

I'm not building anything aimed at "moving" offer acceptance until the measurement is fixed,
because I can't tell if there's a real problem to solve. I'm not deepening job-board integration,
because the data says that channel's limiting factor is applicant fit, not pipeline plumbing. I'm
betting a small amount (1.5 weeks) on testing whether referral quality holds at higher volume,
because the current number is too good to ignore and too small to trust blindly. The bet: fixing
the Job Board funnel and the offer metric will show up in next quarter's numbers faster and more
cheaply than either "do what the VP asked literally" or "do nothing."

## What I'm uncertain about

**Whether there's a real offer-acceptance problem at all.** The two readings (72.2% vs. 83.9%)
have overlapping confidence intervals at n=31–36. I can't tell the board "it's fine" or "it's
broken" with a straight face at this sample size. To find out: fix the `Status`/`Decision On`
instrumentation bug, wait a quarter, recompute on a clean, larger sample.

**What's actually wrong with the 7 off-band offers.** I don't know if `Base CTC`, `Level`, or
`Salary Band` is the field in error — the data can't tell me, and I didn't have time to dig
further in this session. To find out: ask whoever enters offer data whether bands are
auto-populated from `Level` or typed manually per req.

**Whether referral quality is a property of the channel or of the 14 people who use it.** n=8 is
not enough to know if this generalizes. To find out: run the pilot in roadmap item 3, specifically
designed to test quality at 2–3x current volume before committing further.

**What "bring forward the integration work" means to the VP.** If it's a conversion ask, my
verdict stands. If it's an operational-efficiency ask (less recruiter manual work), I haven't
measured that at all, and I should ask before assuming I know what they meant.
