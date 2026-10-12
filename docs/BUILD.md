# Build summary

Everything written for Horizon, what each piece does, and how the pieces find each other.
Written 2026-10-12. **2,578 lines across 21 files**, no dependencies, no build step.

## The four surfaces

| Surface | Lives in | Reader |
|---|---|---|
| Staff dashboard | `condition-cards.html`, published as an Artifact | Provider staff + the clinical reviewer |
| Executive slide | `slides/`, published as a Slides Artifact | Executives |
| Strategy brief | `/condition-brief` skill → `briefs/` | Strategy team |
| Condition card | pipeline → `cards/` → dashboard | Providers, after review |

## The only application code

`condition-cards.html` — 1,006 lines, 60 functions, 37 CSS custom properties, zero
dependencies. One file because it is published as an Artifact page, so there is no bundler
and no module graph. Written in plain ES5-style JS against the Artifact runtime.

| Region | What it does | Why it is shaped that way |
|---|---|---|
| Token system | 37 properties defined three times — bare `:root`, `prefers-color-scheme` guarded by `:not([data-theme="light"])`, and `[data-theme="dark"]` | The viewer's theme has three states, not two; a token defined in only one block renders one theme's text on the other theme's ground |
| PHI screen | 8 regex patterns stripping names-with-titles, ages, dates, phones, record numbers, long identifiers — **before** anything is sent or stored | A free-text box in a clinic receives patient data routinely. Runs first, every time, no exceptions |
| Input normalization | Local map for common abbreviations (`UC`, `afib`, `CHF`), then the page's model access for anything else; returns condition + segment + brand-name detection | Staff do not type canonical names. Resolution is always shown back and correctable — silent correction is how someone reads the wrong card |
| Card renderer | Four blocks (condition, summary, news, drug resources) plus stamps, `Not on this card`, and a non-removable footer | The card's shape is the contract; the renderer refuses to draw a drug row without a source |
| Status states | queued / researching / in_review / returned, driven by the public request document | Staff get honest progress instead of a dead end when no card exists |
| Review queue | Editor-only dock: draft list with verdict badges, fact-check report, two-step clear, send-back with a note | The human gate needed a place to happen |
| Capability boot | Resolves `sample`, `db`, `user`; renders fully before any of them answer and branches on `null` | A capability may never resolve. The page must work anyway |

**What it deliberately cannot do:** generate a card. Its in-page model access has no web
search, so a card written live would be uncited recall — exactly what the gate exists to
stop. Model use is confined to input normalization, a language task.

## Agents — configuration, not code

Five markdown files with frontmatter, in `.claude/agents/`. Claude Code discovers them from
the working directory at session start; there is nothing to register.

| File | Lines | Model | Constrained to |
|---|---|---|---|
| `information-gatherer.md` | 102 | sonnet | Gather and tier facts; never interpret |
| `cardbuilder.md` | 90 | sonnet | Assemble only; **no web tools at all** |
| `factchecker.md` | 94 | opus | Open cited sources; can BLOCK; never edits |
| `inputbuilder.md` | 84 | sonnet | PHI screen, normalize, route |
| `build-qc.md` | 101 | opus | Verify against files; quote lines; never edits |

The tool grants are the enforcement. `cardbuilder` has `Read, Write, Bash` and no
`WebSearch` — it physically cannot research, so it cannot invent what was not gathered.

## The skill

`.claude/skills/condition-brief/` — 288 lines across three files.

- `SKILL.md` (118) — scope fixing, the five-pass fan-out, citation rules, the mandatory
  gaps section, the handoff.
- `references/template.md` (101) — the exact six-section brief skeleton.
- `references/sources.md` (69) — the tier hierarchy and the traps (stale guidelines, press-
  release phase inflation, prevalence figures citing each other in a loop).

Invoked as `/condition-brief <condition>`.

## Data model — where the gate is enforced

Three collections in the dashboard's own store. The separation *is* the security model:

| Collection | Read | Write | Holds |
|---|---|---|---|
| `cards/` | everyone with access | **Editors only** | Cleared cards |
| `drafts/` | **Editors only** | Editors only | Unreviewed card + fact-check report |
| `requests/` | everyone with access | Contributors up | Public status board |

Three consequences worth stating: staff cannot *read* unreviewed clinical content, so it is
invisible rather than merely labelled; staff cannot *write* cards, so no UI bug or impatient
user can put an uncleared card in front of a provider; and the clear action fails closed —
a draft with a missing or unrecognized verdict cannot be cleared at all.

## Scaffolding

```
.claude/agents/            5 agent definitions
.claude/skills/            the brief skill + 2 references
condition-cards.html       the dashboard (publish this)
slides/                    the executive slide: deck.json + slides/cover.html
briefs/                    brief output (.gitkeep — empty dirs do not survive a clone)
cards/                     card output: .md, .json for the store, .review.md
docs/                      SETUP, PRESENTING, REVIEWING, BUILD
```

No `package.json`, no lockfile, no build step, no server, no API keys, no migrations.
Everything is either a markdown file Claude Code reads or an HTML file published as an
Artifact. The dashboard's database is the Artifact's own; capabilities are declared at
publish time, not configured in the repo.

## QC pass

`build-qc` checked the build against the files. One blocking defect, four should-fix, four
minor — all fixed before commit:

- **Blocking:** the verdict check failed open. `verdictClass()` returned `"pass"` for any
  unrecognized verdict, including a missing one, so a draft with no fact-check report would
  have shown a reviewer an enabled clear button and no findings. Now fails closed.
- The PHI titled-name pattern was case-sensitive and missed `Mrs. Alvarez` — the exact
  example in `inputbuilder.md`.
- `condition-cards.html` existed only in a scratch directory while `SETUP.md` told operators
  to publish it. A clone had no dashboard.
- Clearing a card took one click; it now takes two.

## Status

Exercised end to end once: five gatherer passes → cardbuilder → factchecker on type 2
diabetes mellitus. **The fact-check returned BLOCK** with three blocking defects, including
a label URL that pointed at the wrong drug. The draft is in the review queue and cannot be
cleared.

Not yet exercised: a card completing human review; the brief skill on a real condition; any
scheduled refresh of stale cards.
