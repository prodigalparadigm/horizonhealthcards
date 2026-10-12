# What a card costs

Measured on the first real card — type 2 diabetes mellitus, 2026-10-12 — not estimated.
Pricing from the current Anthropic rate card: Sonnet 5 $2.00/$10.00 per MTok in/out,
Opus 5 $5.00/$25.00.

## One card, measured

| Agent | Model | Tokens | Tool calls | Wall | Model cost |
|---|---|---|---|---|---|
| information-gatherer: guidelines | sonnet | 31,023 | 12 | 164 s | $0.082 |
| information-gatherer: approved-therapies | sonnet | 30,452 | 10 | 120 s | $0.080 |
| information-gatherer: pipeline | sonnet | 34,373 | 10 | 149 s | $0.091 |
| cardbuilder | sonnet | 32,319 | 4 | 194 s | $0.085 |
| factchecker | opus | 63,035 | 29 | 469 s | $0.416 |
| **Total** | | **191,202** | **65** | **13.8 min** | **$0.75** |

Gatherers run in parallel, so wall time is the slowest gatherer plus cardbuilder plus
factchecker, not the sum.

**The one assumption.** The harness reports total tokens per agent, not the input/output
split. Agentic loops are input-heavy — context and tool results are resent every turn — so
the table assumes 92% input. Sensitivity: 95/5 gives $0.69, 85/15 gives $0.91. The
figure is stable to within about fifteen cents whichever way the split falls.

**Not included:** orchestration — writing the five agent prompts, reading five reports and
assembling the draft. That runs on Opus in the main session and was not metered separately.
Budget roughly another $0.50–$1.00 per card, less with prompt caching across a batch.

So: **about $1 to $2 of model spend per card, all in.**

## The fact-check is a third of it

Factchecker alone is $0.42 — 33% of model cost, 45% of tool calls, 57% of wall
time. It runs on Opus and it opens every cited source rather than trusting the link. That
is the right place for the money: on this card it caught a label URL pointing at the wrong
drug, an incomplete boxed warning, and an approved indication the card called dubious.
Running that step on Sonnet would save about $0.25 a card. Don't.

## Now scale it to 200

| | Per card | × 200 |
|---|---|---|
| Model spend | ~$1.50 | **~$300** |
| Build time (wall, sequential) | 13.8 min | 46 hours |
| Build time at 8 cards in parallel | — | ~6 hours |
| **Clinical review time** | **5–10 min** | **17–33 hours** |

**Compute is not the constraint.** Three hundred dollars is a rounding error against a
service-line decision. The constraint is the clinician.

At 25 hours of review, one reviewer working two hours a day finishes the catalog in about
three weeks. Apply your own loaded rate for a pharmacist or physician reviewer and review
labour comes out roughly fifteen to twenty times the model spend.

## The number that should actually set the pace

The first card returned **BLOCK** with three blocking defects and ten required fixes.

One card is not a rate. But if anything close to that holds, 200 cards means several
hundred blocking defects to triage, each requiring a correction and a re-review — so budget
review time at **1.5 to 2 passes per card**, not one. That pushes the 25 hours toward 40.

And a queue of 200 unreviewed cards creates pressure to rubber-stamp, which is the one
failure this whole system exists to prevent. A reviewer facing 200 items behaves
differently from one facing 12.

## Recommendation

Release in waves of 10 to 15, drawn from tier 1 of the catalog, sized so a reviewer clears
a wave in a sitting. Measure the block rate over the first two waves. Then decide the pace
with a real number instead of this projection.

Costs are recorded per card on the draft itself and shown in the review queue, so this
table can be rebuilt from actuals rather than re-derived.
