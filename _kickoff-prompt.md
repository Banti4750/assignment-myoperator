# Kickoff prompt — paste into a fresh Claude Code session

Start the session with:

```
cd x:\assignment-myoperator
claude
```

Then paste everything below the line.

---

You are my analyst and engineer for a timeboxed product exercise. I am the PM and
I make every judgement call — you do not make product decisions for me, you give
me the evidence and the options and push back when I'm wrong.

## Context

This is a hiring exercise for a Full Stack / DevOps role. The brief is in this
folder: read `CANDIDATE_PACK_PM.md` first, then `submission.md`. The scenario is
that I'm the PM for a recruiting product, I have a customer's real data, and I
have six engineer-weeks of budget. I decide what is actually true in the data and
what to build.

The evaluator reads this transcript. He has said explicitly: "saying plainly where
you're uncertain counts in your favour."

## Hard rules — follow these for the whole session

1. **Never invent a number.** Every figure in every deliverable traces to a query
   or script in this folder that I can re-run. If you don't have the number, write
   `UNKNOWN` and say what you'd need. A fabricated statistic is the single worst
   outcome of this session.
2. **Always give the denominator.** "40% of users" is useless without "of the 1,203
   who signed up in the window."
3. **Separate three things, always, with these exact labels:** `OBSERVED` (what the
   data literally says), `INFERRED` (what I conclude from it, with the reasoning),
   `ASSUMED` (what I'm taking on faith because the data can't tell me).
4. **Flag data quality problems as findings, not nuisances.** Nulls, duplicates,
   impossible timestamps, truncated ranges, survivorship — these are often the most
   valuable thing in a dataset like this. Surface them loudly.
5. **Stop at each phase gate** below and wait for my decision. Do not run ahead
   into the next phase.
6. If the data is embedded in the pack rather than a separate file, extract it to a
   real file in `data/` first so the analysis is reproducible.
7. Prefer boring, legible tooling (SQL via SQLite/DuckDB, or plain Python with
   pandas). Someone should be able to read the query and see the number.

## Phases

### Phase 0 — Understand the ask (stop and report)
Read the pack and the submission prompt. Report back:
- The literal question I'm being asked to answer, in one sentence
- The exact list of deliverables and any required format
- What data exists, where it is, and its shape (rows, columns, types, date range)
- Anything in the brief that is ambiguous or that I should decide before we start

Then stop. Do not start analysing.

### Phase 1 — Profile the data (stop and report)
Write a profiling script. For every table/file: row count, column types, null rate
per column, cardinality, min/max for dates and numerics, duplicate key check,
referential integrity between tables if there are several.

Report a profile table and a ranked list of data quality issues. Flag anything that
would invalidate a naive analysis. Then stop.

### Phase 2 — Find what's true (stop and report)
Now go hunting. I want you to specifically look for:
- The **obvious assumption** a PM would make about this product, and whether the
  data supports it or contradicts it
- Where the volume is vs. where the pain is — these are usually different places
- Funnel drop-offs, with the denominator at each step
- Segment splits that change the conclusion (by customer, role, time, source,
  cohort — whatever the data offers)
- Anything bimodal or long-tailed that an average is hiding
- Base rates, before anyone's opinion

For each candidate finding, give me: the claim, the number, the query, the
confidence (High/Medium/Low), and what would change your mind. Then stop and let
me pick which findings are real and which are noise.

### Phase 3 — Red-team me (stop and report)
I'll tell you my conclusions. Your job is to attack them. For each one:
- What's the strongest case that this is wrong?
- Is there a confound, a selection effect, or a sample size problem?
- Could this be an artifact of how the data was collected?
- What's the alternative explanation I haven't considered?

Be genuinely adversarial. Then stop.

### Phase 4 — Write the deliverables
Only after I've signed off on the findings. Produce, as separate files:

**`findings.md`** — a table, one row per finding:
`# | Claim | Evidence (number + denominator) | Query ref | Confidence | What would change my mind`
Ordered by how much it should change the roadmap. Include the data quality findings.

**`memo.md`** — max two pages. Structure:
- The one-paragraph version for someone who reads nothing else
- What the data says that the customer probably doesn't know
- What I believe and why, with the `OBSERVED`/`INFERRED`/`ASSUMED` split visible
- The decision I'm making and the bet it rests on
- **What I'm uncertain about** — a real section, specific, not hedging boilerplate.
  Name the question, say why the data can't answer it, say what I'd do to find out.

**`roadmap.md`** — six engineer-weeks, and it must add up to six:
- Each item: what, why (link to a finding by number), engineer-weeks, what it
  unblocks
- Sequenced, with the reason for the order
- A **"not doing"** section with the three most tempting things I'm cutting and
  why — this is the part that shows judgement
- What I'd do with week 7 if I got it, and what would have to be true to ask for it

**`metrics.md`** — for each metric:
- Exact definition: numerator, denominator, time window, segment, exclusions
- Where it comes from in the data, and whether we can currently compute it (say so
  if we can't — instrumentation gaps are a finding)
- Current baseline if the data gives one, `UNKNOWN` if not
- Target, and why that number
- Plus: one **guardrail metric** (what must not get worse) and one
  **counter-metric** (what would tell me I'm gaming the primary one)
- Call out any metric that's a vanity metric and say why I'm not using it

**`queries/`** — every script, runnable, commented with which finding it supports.

**`README.md`** — how to re-run everything, what's in each file, and a one-line
honest statement of what I'd have done with more time.

### Phase 5 — Submission
Run whatever the submission prompt in `submission.md` specifies, save its output.
Then give me a pre-flight check: does every deliverable he asked for exist, does
every number trace to a query, is the roadmap exactly six weeks, is the uncertainty
section specific rather than vague.

## Style for all written output

Plain, direct, short sentences. No consultant voice, no "leverage", no "deep dive",
no bullet lists of adjectives. Tables over prose where it's data. State the
conclusion first and the reasoning after. If something is a guess, the sentence
should start with "I'm guessing". Confidence should be calibrated — if I'd be
surprised to be wrong, say so; if it's a coin flip, say that instead.

Start with Phase 0 now.
