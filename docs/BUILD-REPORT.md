# Horizon — complete build report

Everything built, every decision and why, what is guarded and what is not, what quality
assurance actually found, where the data can live, and how to deploy it.

Written 2026-10-12. Companion documents: [BUILD.md](BUILD.md) (one-page summary),
[COSTS.md](COSTS.md), [STORAGE.md](STORAGE.md), [SETUP.md](SETUP.md),
[REVIEWING.md](REVIEWING.md), [PRESENTING.md](PRESENTING.md),
[TRANSCRIPT.md](TRANSCRIPT.md).

---

## 1. What this is

A health system strategy team asked for a tool that produces a structured briefing on a
medical condition. What got built produces two briefings for two different readers, behind
one research pipeline and one mandatory human review gate.

| Output | Reader | Shape | Status |
|---|---|---|---|
| Strategic brief | Strategy team | Six sections: standard of care, emerging treatments, key players, system implications, watch list, gaps | Skill written, never run |
| Condition card | Clinical provider | One page: condition, summary, recent changes, drug resources | 9 drafted, 0 released |

**Nothing has been released to a provider.** Six cards have been fact-checked and all six
were blocked. That is the system working as designed, and section 5 is the detail.

---

## 2. Scaffolding

```
.claude/
  agents/                     5 agent definitions, discovered by Claude Code at session start
    information-gatherer.md     research, one pass at a time, primary sources only
    cardbuilder.md              assembles cards; NO web tools, deliberately
    factchecker.md              opens every cited source; can BLOCK
    inputbuilder.md             PHI screen, input normalization, routing
    build-qc.md                 verifies the build against the files; never edits
  skills/condition-brief/
    SKILL.md                    the strategy brief protocol
    references/template.md      the six-section skeleton
    references/sources.md       source tier hierarchy and traps
condition-cards.html          the staff dashboard, published as an Artifact (1,335 lines)
data/conditions.json          200-condition catalog: ICD-10, category, tier, aliases
slides/                       the executive deck: deck.json + 5 slide files + fonts
demo_deck.pdf                 the deck, print-ready
cards/                        9 drafted cards: .md, .json, and .review.md where checked
briefs/                       brief output (.gitkeep — empty dirs do not survive a clone)
docs/                         this report and its companions
```

**No build step, no dependencies, no server, no API keys, no migrations.** Everything is
either a markdown file Claude Code reads or an HTML file published as an Artifact. There is
deliberately nothing to install, which is also why there is currently nothing App Runner can
deploy (section 7).

### The pipeline

```
          staff types a condition
                    │
             [ inputbuilder ]           PHI screen → normalize against the 200-catalog → route
                    │
     ┌──────────────┴──────────────┐
cleared card                 no card yet
served instantly                   │
                      [ information-gatherer ]      one composite `card` pass, or five
                                   │                 separate passes for a strategy brief
                      ┌────────────┴────────────┐
                [ cardbuilder ]          condition-brief skill
                 one-page card             six-section brief
                      │                           │
                      └────────────┬──────────────┘
                                   │
                           [ factchecker ]          opens every cited source
                      PASS · PASS WITH FIXES · BLOCK
                                   │
                        human reviewer releases it
                                   │
                           visible to staff
```

---

## 3. Decision points

Each of these was a real fork. The alternative is recorded because the reasoning matters more
than the choice.

| # | Decision | Chosen | Rejected, and why |
|---|---|---|---|
| 1 | Form factor | Claude Code skill + agents in a repo | A standalone Python CLI with the Claude API (more plumbing, API keys, no faster to working); a hosted web app only (no auditable artifact) |
| 2 | Evidence posture | Cite every claim, flag every gap | Cite key claims only; narrative with appended sources. Rejected because a card a reviewer cannot audit cannot be reviewed |
| 3 | Who researches | Separate gatherer agents, one pass each | One agent doing everything. Separation keeps provenance clean and lets passes run in parallel |
| 4 | Can the builder research? | **No. `cardbuilder` has no web tools at all** | Giving it search. Denying the capability is stronger than instructing it not to invent — it cannot exceed what was gathered |
| 5 | Who checks | A separate `factchecker` on Opus that opens sources and can block | Self-review by the builder. A reviewer who wrote the thing cannot review it |
| 6 | Can the checker edit? | **No. It reports; someone else fixes** | Letting it fix what it finds. Then nobody reviews the fix |
| 7 | Can the dashboard generate a card live? | **No** | Live generation. The page's model access has no web search, so a live card would be uncited recall — precisely what the gate exists to stop. Model use is confined to input normalization, a language task |
| 8 | Where is the gate enforced | **In the data layer.** `cards` is write-restricted to Editors | UI-only enforcement. A UI bug, a misconfiguration or an impatient user then defeats it |
| 9 | Are unreviewed cards visible to staff? | **No — unreadable, not merely labelled** | Showing them with a warning banner. A label can be missed; an unreadable collection cannot |
| 10 | What do staff see while waiting? | A public status board: queued → researching → in review → returned | Nothing, or the draft. The first is a dead end, the second defeats the gate |
| 11 | Release mechanics | Two deliberate clicks, and **fail closed** on a missing verdict | One click, and treating an unrecognized verdict as a pass. Both were in the first build; QA found the second (section 5) |
| 12 | Reviewer disagrees with the check | A **dispute** path that records it and never releases | An override. On provider-facing clinical content, disagreement routes to a second opinion, not to staff |
| 13 | PHI in the input box | Screen and strip before anything is sent or stored | Trusting staff not to type it. A free-text box in a clinic receives patient data routinely |
| 14 | Catalog provenance | 200 conditions, editorial, **explicitly not a ranked claims extract** | Claiming it is "the top 200." It is not, and saying so would be the kind of unsourced confidence this system exists to prevent |
| 15 | Catalog location | Shipped inline in the page | A `catalog` collection in the store. Static reference data does not need shared mutable state — but this means changing the 200 requires a republish |
| 16 | Card production cadence | Waves of 10–15 | A 200-card bulk run. 200 unreviewed cards creates pressure to rubber-stamp, which is the one failure the system exists to prevent |
| 17 | Research passes per card | One composite `card` pass instead of three | Three separate passes. Roughly a third of the cost for the same card; briefs still use five |
| 18 | Repo visibility | **Private** | Public. It holds nine clinical drafts carrying six BLOCK verdicts |

---

## 4. Guardrails

### Enforced by capability — cannot be instructed away

| Guardrail | Mechanism |
|---|---|
| The builder cannot invent beyond gathered material | `cardbuilder` tool grant is `Read, Write, Bash`. No `WebSearch`, no `WebFetch` |
| Staff cannot publish a card | `cards` collection is `write: "admin"` in the published capability declaration |
| Staff cannot read unreviewed clinical content | `drafts` collection is `read: "admin"` |
| Staff can still request a card | `requests` is `write: "interact"` — Contributors and up |
| QA cannot quietly fix what it reviews | `build-qc` and `factchecker` are read-only by instruction and report-only by output contract |

### Enforced in the page

- **Release fails closed.** Only an explicit `PASS` or `PASS WITH FIXES` can be released. A
  missing, empty or unrecognized verdict disables the button and badges the draft `No verdict`.
- **Two-step release.** The first click arms, the second releases.
- **A blocked card explains itself in visible text**, not a tooltip, and offers dispute as a
  real alternative action.
- **PHI screen runs first**, on every submission, before normalization or storage. Eight
  patterns: titled names, ages, dates, phones, record numbers, long identifiers, SSN.
- **The clinical-reference footer is unconditional** — not removable by any code path.
- **Resolution is always shown back** and correctable. Silent correction is how someone reads
  the wrong card without knowing.
- **Staleness is surfaced** at 90 days on every card's as-of stamp.

### Enforced in the agent specs

- **Tier 4 is a lead, never a citation.** Trade press must be chased to the filing, the trial
  record or the label.
- **A URL you have not opened is not a citation.** Added after a metformin row cited a label
  that turned out to be a two-drug combination product.
- **Confirm the cited label is representative** — right drug, right strength, right
  formulation, and the route on the row matches the label.
- **"No boxed warning" is a claim and needs the same proof as a warning.** Added after three
  agents on one card were printed as unboxed when all three carry boxed warnings.
- **Never convert "unconfirmed" into "none."**
- **Never print a boxed warning's substance while labelling the row unboxed.**
- **Boxed warnings and major contraindications are mandatory** on any listed agent.
- **A gaps section is mandatory and never empty.** If it is empty, the research did not look
  hard enough.
- **Never cite a guideline without its year or version.**

### Not guarded — known holes

- **No schema validation.** Nothing checks a card's JSON against the shape the renderer
  expects. QA found two cards inventing keys (`cutForSpace`, `cutDrugs`) that the renderer
  silently drops, which made two MRSA agents invisible on a pneumonia card.
- **No automated tests and no CI.** Every check in this report was performed by an agent or
  by hand.
- **The 8-row card cap can beat coverage completeness.** It did: a CAP card dropped vancomycin
  and linezolid to stay under the cap. A formatting limit should never outrank clinical
  coverage, and that ordering is not yet encoded anywhere.
- **No audit-log export.** Release events carry a name and date on the card; there is no
  exportable log.
- **No scheduled refresh.** Staleness is flagged, never acted on.
- **Guideline text is copyrighted.** FDA labeling is US-government work and freely
  reproducible; society guidelines (ACC/AHA, GOLD, KDIGO, GINA, IDSA/ATS, ADA) are not.
  Cards paraphrase and cite, which is the right posture, but **nobody has reviewed this for
  reproduction limits** and that review is needed before anything is published beyond the
  institution.

---

## 5. QA analysis

Two layers ran: `build-qc` over the build itself, and `factchecker` over each card.

### 5.1 Build QC

One blocking defect, four should-fix, four minor. All fixed before the first commit.

**Blocking — the gate failed open.** `verdictClass()` returned `"pass"` for any verdict it did
not recognize, including a missing one. A draft written without a fact-check report would have
shown a reviewer an enabled release button and no findings to read — the single path by which
unchecked clinical content could reach a provider through the intended UI. It now fails closed.

Also fixed: a PHI pattern that was case-sensitive and therefore missed `Mrs. Alvarez`, the
literal example in its own specification; the dashboard existing only in a scratch directory
while the setup doc told operators to publish it; one-click release; a review queue that never
refreshed.

### 5.2 Card fact-checks — six run, **six blocked**

| Card | Verdict | Blocking | Fixes | Headline defect |
|---|---|---|---|---|
| Type 2 diabetes | BLOCK | 3 | 10 | Metformin label link resolved to a two-drug combination product |
| Atrial fibrillation | BLOCK | 3 | 7 | Three agents printed as carrying no boxed warning; all three carry one |
| Major depressive disorder | BLOCK | 4 | 6 | Esketamine boxed warning omitted respiratory depression |
| Measles | BLOCK | 6 | 9 | IGIV dose given as a range whose low end is a four-fold underdose |
| Community-acquired pneumonia | BLOCK | 2 | 6 | The only MRSA-looking agent is MSSA-only for this indication; the two real ones were invisible |
| Hypertension | BLOCK | 2 | 6 | Spironolactone row cites a 2014 label that flags its own obsolescence and omits hyperkalemia |

**A 6-of-6 block rate on a first wave is the most important number in this report.** It says
the research-and-build stage is not trustworthy on its own, and that the gate is not
ceremonial. It also means review effort should be budgeted at **1.5–2 passes per card**, not
one.

### 5.3 Defect taxonomy

Twelve recurring classes, each with a real instance. This is the most reusable output of the
whole exercise.

| # | Class | Instance |
|---|---|---|
| 1 | **Wrong document cited** | Metformin → Segluromet (ertugliflozin + metformin). Metoprolol → a 12.5 mg SPL under a brand not marketed at that strength, which happens to lack the boxed warning. Auvelity → a label predating the indication cited two lines above it |
| 2 | **Absence asserted without verification** | Dofetilide, sotalol, metoprolol, GamaSTAN all printed as "no boxed warning"; all four carry one |
| 3 | **Incomplete boxed warning** | Esketamine missing respiratory depression — the reason pulse oximetry is required. Metformin missing age 65+ and iodinated contrast. Canagliflozin missing Fournier's gangrene |
| 4 | **Stale label cited as current** | Spironolactone's 2014 PDF, which says on its face "may not be the latest approved by FDA." Duloxetine's 2010 label, 16 years old |
| 5 | **Date errors** | Baxdrostat 2026-05-18 vs 2026-05-15 actual. Auvelity dementia indication "2025" vs 2026-04-30. A REMS item 15 months stale |
| 6 | **Dosing error** | IGIV measles PEP as "100–400 mg/kg"; the source says 400 mg/kg. The low end is a four-fold underdose |
| 7 | **Over-absolute negative** | Measles card: "no pipeline antiviral to list." Its own source has a ribavirin section — off-label, EIND for IV |
| 8 | **A hedge becoming misinformation** | Diabetes card marked the Ozempic CKD indication "unverified." It is approved and documented in the label the card itself cites |
| 9 | **Renderer silently dropping content** | `cutForSpace` and `cutDrugs` are not in the renderer's key whitelist, so vancomycin and linezolid vanished from a CAP card |
| 10 | **Misclassification** | Ceftaroline labelled "anti-MRSA cephalosporin" on a CAP card; its CABP indication covers methicillin-**susceptible** isolates only |
| 11 | **Orchestrator spec errors** | The esketamine review brief listed four boxed-warning components; the label has five. "Reaffirmed 2015" was passed to a builder unsourced. Both originated with the orchestrator, not the agents, and the factchecker caught both |
| 12 | **Internal contradiction** | The AF card asserts first-line ablation as fact in its summary while its own gaps section calls that claim Tier 4 only |

### 5.4 What the checks also confirmed

Not everything failed, and the pattern matters: the clinical cores were largely sound and the
defects clustered in provenance.

- Every antidepressant row carried the class suicidality boxed warning, verified against
  eight separate labels.
- Fluoroquinolone boxed warnings were complete and accurate on all four elements — the
  pneumonia card's *declared* weak point turned out to be clean.
- The 2025 AHA/ACC hypertension guideline checked out in **all six** specifics, including the
  three-first-line-class framing and PREVENT replacing the Pooled Cohort Equations.
- The APA has no current MDD guideline — confirmed against psychiatry.org's own index. The
  most useful finding on that card was correct.
- Measles vitamin A dosing matched CDC exactly; case counts matched to the digit.
- No fabricated drug, dose, trial ID or URL was found on any card.
- Every footer clinical-reference line was present; no card contained patient-directed advice.

---

## 6. Data storage options

Current state and its gaps are in [STORAGE.md](STORAGE.md). The options, with honest
tradeoffs:

| Option | Good for | Cost of it |
|---|---|---|
| **Artifact database** (today) | Authoring and review. Zero setup, live updates to every open page, access via artifact sharing | Vendor-hosted, claude.ai identity not your IdP, no BAA/SLA/retention control, 25,000-document cap, no audit export |
| **Git repo as system of record** (recommended) | The auditable record. Review maps onto PR approval, which carries institutional identity. Diffable, revertable, already in place | Not a serving layer. Needs something in front of it for providers |
| **Static site from the repo** | Cheapest real delivery. S3 + CloudFront, or App Runner serving a built site. No backend, no database, nothing to patch | Read-only. No auth unless you put SSO in front. Rebuild to publish |
| **App Runner + small service** | Real auth, request logging, per-user audit trail, dynamic queries | A service to own, patch and monitor. Needs a container or a supported runtime, neither of which exists in this repo yet |
| **DynamoDB or RDS behind that service** | Durable, backed up, in your account and your region, exportable audit log | Schema and migrations to own. Overkill for 200 documents that change weekly |
| **SharePoint / intranet CMS** | Already has your SSO, retention policy and records management. No new vendor | Manual publishing unless automated; weak diffs; cards stop being versioned artifacts |
| **EHR integration (Infobutton / SMART on FHIR)** | Cards surface where clinicians already are. Highest adoption | Much larger project, clinical informatics governance, and a regulatory conversation this build has not had |

**Recommendation:** git as the record, a static site generated from it for delivery, your SSO
in front, and the Artifact kept as the authoring and review workbench. That keeps every
provider-facing byte on infrastructure you control, and nothing in the clinical path depends
on a vendor surface.

---

## 7. Quick deployment guide

### 7.1 What exists today

```bash
git clone https://github.com/prodigalparadigm/horizonhealthcards
cd horizonhealthcards
claude                         # agents and skills are discovered automatically
/condition-brief heart failure # produces briefs/YYYY-MM-DD-heart-failure.md
```

The dashboard is published as an Artifact with the capability declaration in
[SETUP.md](SETUP.md) §4. Share it with staff as **Contributor** and reviewers as **Editor** —
Viewers cannot request cards, which is the most common setup mistake.

### 7.2 The POC — front end plus limited backend

Built and smoke-tested. An Express server serving a self-contained front end and a
read-mostly JSON API over the card files. **No database**: cards are files, loaded at boot.

```
server/
  package.json          express only
  server.js             API + static host
  public/index.html     the POC front end
Dockerfile              node:22-alpine, health check, serves on $PORT
apprunner.yaml          source-based build config
.dockerignore
scripts/merge-reviews.py  puts the fact-check verdicts into the card JSON
```

| Endpoint | Returns |
|---|---|
| `GET /healthz` | App Runner health probe: card count, catalog count, demo flag |
| `GET /api/catalog` | All 200 conditions with ICD-10, tier, aliases, and the basis statement |
| `GET /api/cards` | Servable cards, summary fields |
| `GET /api/cards/:slug` | One full card |
| `GET /api/drafts` | The review queue with verdicts and defect counts |
| `GET /api/drafts/:slug` | One draft with its full fact-check findings |
| `GET /api/resolve?q=` | Catalog resolution — `afib` resolves to atrial fibrillation |
| `POST /api/requests` | Logs a request for an uncarded condition (in memory) |

The front end keeps the PHI screen client-side and resolves conditions against the catalog
**without a model**, which is both cheaper and more predictable than the Artifact version.

**`SERVE_DEMO` is the switch that matters.** Set to `true` it serves drafts and flags every one
of them `demo`. Set to `false` it serves only `status == "cleared"` — which today is nothing.
In anything other than a demo, that variable is `false`.

Run it locally:

```bash
cd server && npm install --omit=dev
PORT=8099 SERVE_DEMO=true node server.js
curl localhost:8099/healthz
```

### 7.3 Deploying to App Runner

**Image-based (recommended — the Dockerfile is the tested path):**

```bash
AWS_REGION=us-east-1
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
REPO=horizon-health-cards

aws ecr create-repository --repository-name $REPO --region $AWS_REGION
aws ecr get-login-password --region $AWS_REGION \
  | docker login --username AWS --password-stdin $ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com

docker build -t $REPO .
docker tag $REPO:latest $ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO:latest
docker push $ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO:latest
```

Then point the App Runner service at that image, port **8080**, health check path
**`/healthz`**. If a service already exists, `aws apprunner update-service` with the new image
identifier rather than creating a second one.

**Source-based:** connect the repo via an App Runner GitHub connection — a private repo needs
that connection authorised once in the console — and App Runner reads `apprunner.yaml`.

**Two things to decide before this is more than a demo:**

1. **Authentication.** App Runner has no built-in auth. The service is public once deployed.
   Put CloudFront with Cognito or your IdP in front, or an ALB with OIDC, before any real
   clinician-facing use.
2. **`SERVE_DEMO=false`.** With it true, the deployed service publishes blocked drafts. That
   is intended for a demo and wrong for anything else.

### 7.4 Rebuilding the deck PDF

See [../slides/README.md](../slides/README.md). The fonts are committed on purpose: headless
Chrome does not reliably fetch Google Fonts during a print run, and the first build silently
fell back to Arial on every slide while still looking plausible.

---

## 8. Things not asked for, worth deciding

1. **Who signs off clinically, by name, and under what authority?** The system records a
   releaser. It does not establish who is permitted to be one.
2. **Guideline copyright.** FDA labeling is freely reproducible; society guidelines are not.
   Cards paraphrase and cite, which is defensible, but this has had no legal review.
3. **Regulatory posture.** This is positioned as an informational reference, not clinical
   decision support, and every surface says so. Whether that positioning holds under scrutiny
   is a question for your regulatory group, not for me or for a disclaimer line.
4. **Retention and discoverability.** Released cards are clinical reference material staff
   relied on at a point in time. They are plausibly discoverable in litigation. Nobody has
   set a retention period.
5. **Metrics worth tracking from day one:** block rate per wave, time from request to release,
   proportion of cards past 90 days, which conditions get requested but never carded, and
   disputes raised per reviewer.
6. **Reviewer capacity is the real constraint**, not compute — 17–33 hours for the catalog at
   one pass, closer to 40 at the 1.5–2 passes the block rate implies. One named reviewer with
   standing time is the ask.
7. **Second-reviewer policy.** The dispute path routes to a second opinion. That second
   reviewer does not exist yet.
8. **No accessibility audit** has been run on the dashboard.
9. **Cards are US-centric** — FDA labels, US guidelines, Medicare framing. Nothing marks that
   assumption on the card itself.
10. **The catalog's ICD-10 codes are reference values** and have not been reconciled against
    your own code set.

---

## 9. Cost, measured

Full method in [COSTS.md](COSTS.md). Measured, not estimated: **~26 agent runs, ~1.19 million
subagent tokens, roughly $4.50 of model spend** for nine cards researched and built and six
fact-checked. That works out to about **$0.50 to build a card and $0.38 to check one**, plus
orchestration, which was not metered separately.

Extrapolated to the 200-condition catalog: **about $300 of model spend** against **17–40 hours
of clinician review**. Review labour runs fifteen to twenty times compute. Compute is not the
constraint and should not be optimized first.

The fact-check is a third of per-card model cost and runs on the most capable model. On the
evidence in section 5, that is the best-spent money in the pipeline.
