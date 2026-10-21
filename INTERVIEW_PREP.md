# Interview prep — questions I should expect, and where to find the answer

Built from the actual weak points this session surfaced: places where a number was
contested, a sample was thin, a definition was ambiguous, or I (the PM) deferred a
judgment call instead of making it myself. An evaluator reading the transcript has
everything they need to ask these. Each question links to where the material lives.

## On the two verdicts (D1)

1. **"Your job-board verdict rests on 'ties for most hires.' Walk me through why 7/26
   isn't just noise — couldn't one hire either way flip the ranking?"**
   It can, and it did change by 1 when I excluded the 6 duplicate-candidate rows
   (7→6, `findings.md` #1). The verdict doesn't actually rest on the tie-breaking —
   it rests on the volume/conversion split (#2) and the interview→offer bottleneck
   (#3), which are far more robust. Be ready to say the tie is a red herring and
   point to the real evidence.

2. **"You said the offer-acceptance number might not even be a real problem. If you're
   wrong and it is real, what did your roadmap lose by not acting on it this quarter?"**
   Be honest: if 72% is the true rate, I lost a quarter on a comp/process fix.
   The defense is in `roadmap.md`'s "not doing" section — I'm explicitly trading a
   possible quarter of delay against not building an intervention for a problem I
   can't confirm exists on n=31. Know this trade-off cold; don't discover it live.

3. **"What did the VP actually mean by 'bring the integration work forward'? Did you
   ask?"** No — I didn't ask, I inferred it meant a conversion fix and said so as an
   explicit `ASSUMED` in `memo.md`. If challenged, say plainly: this is the one place
   I'd go back to the VP before committing engineering time, and I flagged it as such.

## On sample size and statistics

4. **"You ran a 95% CI on 26/36 vs 26/31 and found they overlap. Do you actually know
   what that calculation assumes, or did the tool just output a number?"**
   It's a simple Wald/normal-approximation CI (`p ± 1.96·√(p(1-p)/n)`), not a proper
   two-proportion significance test. At n=31 with p near 0.84, the normal
   approximation is already shaky (not enough room from 1.0). Say this plainly if
   asked — the right answer isn't "they're definitely not different," it's "I don't
   have enough data to tell, and a rougher check confirms that."

5. **"Referral's 87.5% hire rate — would you bet your job on that number?"**
   No, and I said so (`findings.md` #8, Medium confidence, n=8). Be ready to say why
   I still funded a 1.5-week pilot on a number I don't trust: the downside of being
   wrong is small and contained, the pilot is designed to produce the larger sample
   that would let someone trust it next quarter.

## On data quality (D4 — the highest-weighted deliverable)

6. **"You found that 7 of 36 offers have a base salary outside the job's own salary
   band, by up to 6x. That's a huge finding and it's buried at the bottom of your
   findings table. Why?"** Honest answer: I found it in the last hour, while building
   the metrics spec, not during the dedicated data-quality phase. It should probably
   rank higher. Don't defend the ordering — concede it and say what you'd do
   differently (go find the root cause instead of flagging and moving on).

7. **"Is the duplicate-candidate problem (12 of 300 rows) a dedup bug, or could these
   genuinely be two different people with the same name and phone number?"**
   I treated it as "likely duplicate" based on name+phone match, but never got
   confirmation — this is `ASSUMED`, not `OBSERVED`. If pushed, say what evidence
   would settle it (matching on a third independent field, or asking Acme directly).

8. **"Why did you decide the duplicate Application IDs were a one-time seed artifact
   and not an active bug?"** Because all 8 colliding rows share one identical
   `created_time` timestamp (`queries/14_redteam_checks.py` §6) — a live bug would
   produce collisions spread across many timestamps. Know this specific piece of
   evidence; it's the only thing separating "ignore it" from "treat it as urgent."

## On process (this is probably where I'm weakest)

9. **"At two points you told Claude to use its own defaults and pick which findings
   were real, instead of deciding yourself. The brief said that's explicitly your
   call. Why did you hand it over?**" This is in `PROCESS.md` section 2, stated
   plainly, not hidden. Have an actual answer ready — not "I trusted the tool," but
   what you'd do differently with more time, and which of the deferred calls you'd
   take back first if you could.

10. **"Which finding would you have found yourself, without the tool, if you'd just
    opened the data in a spreadsheet?"** Good one to have a real answer to — probably
    the raw funnel counts (#9) and the source-level volume split (#2), since those
    are a pivot table away. The things you likely wouldn't have caught by hand: the
    duplicate-ID batch-timestamp pattern (#10), the CI overlap on the acceptance
    rate (#4), and the off-band CTC outliers (#7) — those needed the systematic
    pass, not inspection.

## The three questions already waiting for you

`PROCESS.md` ends with three questions left blank on purpose — answer them before
you send this, not during the interview:
- What did I get wrong first, and what made me notice?
- Which of my numbers would I least like to defend, and why?
- What would I have asked the hiring manager if I could?

My own candidate answer to the second one, if you want a starting point: **the offer
acceptance baseline (83.9%, n=31)**. It's the number most load-bearing for D1's second
verdict, and it's the one with the widest confidence interval relative to how
confidently the memo states it.
