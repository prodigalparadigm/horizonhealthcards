---
name: condition-brief
description: Generate a sourced strategic briefing on a medical condition for a health system strategy team — current standard of care, emerging treatments in development, key companies and institutions, and what each implies for the system. Use when the user says "brief me on <condition>", "/condition-brief", "what's the pipeline in <disease>", "standard of care for <condition>", "horizon scan <condition>", or is sizing up a service line, an affiliation, or a drug-spend exposure in a disease area. Do NOT use for individual patient care decisions, for coding/billing questions, or for a general literature review with no strategic question behind it.
---

# Condition Brief

Produce one dated, fully sourced briefing on a medical condition, written for a health
system strategy team that has to make capital, service line, workforce, and contracting
decisions — not for clinicians at the bedside.

**Every factual claim carries an inline source. Every gap is named out loud.** That rule
is the product. A brief that reads well but can't be audited is a failed brief here.

## Not clinical guidance

This brief informs institutional strategy. It is not clinical decision support and must
not be used to direct the care of an individual patient. Carry that line into the output
header, every time.

## Step 1 — Fix the scope before searching

Conditions arrive vague. "Heart failure," "breast cancer," and "IBD" each fan out into
segments with different standards of care, different pipelines, and different economics.

Do not stop and ask. Pick the clinically meaningful segmentation yourself, state it in
the Snapshot as an explicit assumption, and proceed. Examples:

- "heart failure" → segment HFrEF / HFpEF, note that the brief leads with whichever has
  the livelier pipeline, and say so
- "breast cancer" → segment by receptor status (HR+/HER2−, HER2+, TNBC) and stage
- "ulcerative colitis" → moderate-to-severe is where the pipeline lives; say that

If the user named a segment, honor it exactly and do not widen it.

Also fix the **geography and payer frame**: default to US practice, FDA regulatory
status, and US commercial/Medicare reimbursement unless the user says otherwise. State
the default in the header.

## Step 2 — Fan the research out to information gatherers

You do not run the searches yourself. Spawn five `information-gatherer` subagents **in a
single message** so they run concurrently — one per pass. Each returns sourced structured
findings; none of them interprets anything. You do the interpreting in Step 3.

| Pass | Agent prompt covers |
|---|---|
| `guidelines` | Current society guideline(s), year/version, algorithm by line, practice divergence |
| `approved-therapies` | FDA-approved agents by line, labels, approval dates, route and site of care |
| `pipeline` | Phase 2/3 assets, mechanism, sponsor, trial IDs, readout and PDUFA dates, failures |
| `players` | Sponsors, device makers, centers of excellence, trial networks, deals with values |
| `economics` | Price, reimbursement pathway, J-code status, site-of-care rules, prior auth posture |

Each gatherer spends 4–6 searches, so the brief costs roughly **20–30 searches total.**
That is the budget. If a pass comes back thin, re-task that one gatherer with
`SendMessage` — its context is still live and it already knows the segment — rather than
spawning a fresh one that has to relearn the scope.

Brief each gatherer like a peer. Give it:

- the exact condition segment you fixed in Step 1, verbatim
- its pass name
- the geography and payer frame (default: US, FDA, Medicare/commercial)
- anything a prior brief in `briefs/` already established, so it does not re-derive it

What you must not do: hand a gatherer your hypothesis. "Confirm that oral agents are
displacing infusions" comes back confirmed whether or not it is true. Ask instead for
route of administration by asset and decide for yourself.

Read `references/sources.md` before briefing them so your prompts name the right primary
domains for this disease area.

## Step 3 — Write the brief

Follow `references/template.md` exactly — its six sections, in its order. Write to:

```
briefs/YYYY-MM-DD-<condition-slug>.md
```

Use today's real date. Never overwrite an existing brief for the same condition: a
second brief on the same day gets a `-v2` suffix, and a brief on a later date stands
alongside the earlier one so the team can read the delta.

### Citation rules

- Inline markdown link immediately after the claim it supports: `[(NCCN v3.2025)](url)`.
- Every pipeline table row carries a source. No exceptions, no "see above."
- Label each source's tier when the tier is anything other than Tier 1 or 2 — a company
  press release and a society guideline must not look alike on the page.
- Attach a date to anything that moves: approval dates, guideline versions, trial phase
  as-of dates, deal announcement dates.

### The gaps section is mandatory

Section 6 ends with **"Could not confirm."** It is never empty — if it is, you did not
look hard enough. List, as bullets:

- claims you found only in secondary sources and could not run to a primary one
- numbers that conflict across sources, with both numbers and both sources
- questions a strategy team will ask that this brief cannot answer
- anything whose freshness you doubt

Write it plainly. "Enrollment completion date not posted; last ClinicalTrials.gov update
2025-11" beats a hedge.

### Voice

Short declarative sentences. Tables for anything with more than three parallel items.
No consulting filler — cut "it is important to note," "in today's rapidly evolving
landscape," and every sentence that could precede any brief on any condition. A strategy
VP should be able to read the Snapshot and Implications and walk into a meeting.

## Step 4 — Hand it off

Report in chat: the file path, the segment scope you assumed, the search count you spent,
and the single most consequential thing in the brief. Then stop. Do not paste the brief
into chat — it lives in the repo, and the team reads it there.
