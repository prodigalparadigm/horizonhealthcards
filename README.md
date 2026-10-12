# Horizon

Condition intelligence for a health system. One research pipeline feeds two very different
readers, and one review gate stands between the research and anybody who treats patients.

| Output | Reader | Shape |
|---|---|---|
| **Strategic brief** | Health system strategy team | Six sections: standard of care, emerging treatments, key players, system implications, watch list, gaps |
| **Condition card** | Clinical provider | One page: condition, quick summary, quick news, current drug resources |

```
                 staff types a condition
                           │
                    [ inputbuilder ]        PHI screen → normalize → route
                           │
        ┌──────────────────┴──────────────────┐
   cleared card                        no card yet
   served instantly                          │
                              [ information-gatherer ] ×5, in parallel
                               guidelines · approved-therapies
                               pipeline · players · economics
                                           │
                        ┌──────────────────┴──────────────────┐
                 [ cardbuilder ]                     condition-brief skill
                  one-page card                       six-section brief
                        │                                     │
                        └──────────────┬──────────────────────┘
                                       │
                               [ factchecker ]
                            PASS · PASS WITH FIXES · BLOCK
                                       │
                            human reviewer clears it
                                       │
                            cleared → visible to staff
```

## The agents

| Agent | Model | Job | Deliberately cannot |
|---|---|---|---|
| `information-gatherer` | sonnet | One research pass, facts chased to a primary source and tiered | Interpret, recommend, synthesize |
| `cardbuilder` | sonnet | Assemble the one-page card from gathered findings | Search — it has no web tools |
| `factchecker` | opus | Independently open every cited source; clear or block | Edit the card it reviews |
| `inputbuilder` | sonnet | Screen PHI, normalize messy input, route, own the dashboard | Build cards |
| `build-qc` | opus | QC the whole build against the actual files before a demo or handoff | Edit what it reviews |

Source tiers run 1 (FDA labels, society guidelines) to 4 (trade press).
**Tier 4 is a lead, never a citation** — see
[`sources.md`](.claude/skills/condition-brief/references/sources.md).

## Quick start

```bash
# a six-section strategic brief
/condition-brief ulcerative colitis
```

Cards are requested from the dashboard, built by the pipeline, and then held for human
review. Nothing reaches staff until a reviewer clears it.

## Repository layout

```
.claude/
  agents/                      information-gatherer, cardbuilder, factchecker,
                               inputbuilder, build-qc
  skills/condition-brief/      the strategy brief: protocol, template, source tiers
condition-cards.html           the staff dashboard — publish this as an Artifact
slides/                        the executive slide — publish as a Slides Artifact
briefs/                        generated strategic briefs, dated
cards/                         generated condition cards (.md, .json, .review.md)
server/                        POC: Express API + front end (see docs/BUILD-REPORT.md)
Dockerfile · apprunner.yaml    container and App Runner config
scripts/merge-reviews.py       writes fact-check verdicts into the card JSON
demo_deck.pdf                  the executive deck, print-ready
docs/
  BUILD-REPORT.md              complete build description — scaffolding, decisions,
                               guardrails, QA analysis, storage options, deployment
  TRANSCRIPT.md                what was asked and built, session by session, errors included
  BUILD.md                     what was built, one page
  SETUP.md                     install, deploy, permissions, troubleshooting
  PRESENTING.md                presenter quickstart for the executive slide
  REVIEWING.md                 for the clinician or pharmacist clearing cards
```

## Three design decisions worth knowing

1. **The dashboard cannot generate cards.** Its in-page model access has no web search, so
   a card written live would be uncited recall — exactly what the fact-check gate exists to
   stop. The page serves cleared cards and queues everything else. In-page model use is
   limited to input normalization, which is a language task, not a clinical-fact task.
2. **The gate is enforced in the data layer, not by convention.** The `cards` collection is
   write-restricted to Editors. Staff physically cannot publish a card, whatever the UI does.
3. **Unreviewed work is invisible, not merely unlabeled.** Drafts live in a separate
   collection that staff cannot read. Staff see a status — queued, in review — never the
   unreviewed content.

## Boundary

Briefs inform institutional strategy. Cards are an informational clinical reference
assembled from FDA labeling and published society guidelines. **Neither is clinical decision
support, and neither is for the care of an individual patient.** The dashboard screens
patient information out of its input and does not store it.

## Status

**This is a POC/demo build.** Nine condition cards exist as drafts. Six have been
fact-checked and **all six were blocked**, with 20 blocking defects between them — see
[`docs/BUILD-REPORT.md`](docs/BUILD-REPORT.md) §5 for the analysis and the 12-class defect
taxonomy. For the demo those drafts are served anyway, each flagged `demo`, with its real
fact-check findings visible in the review queue.

**No card has passed review.** Nothing here is fit for clinical use. Set `SERVE_DEMO=false`
and the service correctly serves nothing at all.

Full account of what was built and what went wrong: [`docs/TRANSCRIPT.md`](docs/TRANSCRIPT.md).
