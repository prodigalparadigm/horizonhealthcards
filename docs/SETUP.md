# Setup

For whoever installs and operates Horizon. Reader assumed comfortable with a terminal and
with Claude Code; no knowledge of the pipeline assumed.

## 1. Prerequisites

- **Claude Code** installed and signed in to an account that can publish Artifacts.
- The repository cloned anywhere; nothing is path-dependent.
- Web search available to the session. The gatherer agents are useless without it.
- No API keys, no services, no database to stand up. The dashboard's store is the
  Artifact's own.

## 2. Install

```bash
git clone <this repo>
cd horizon
claude
```

Claude Code discovers `.claude/agents/*.md` and `.claude/skills/*/SKILL.md` automatically on
session start. Confirm with:

```
/condition-brief
```

If the skill does not appear, you are running Claude Code from outside the repository root —
agent and skill discovery is relative to the working directory.

## 3. Generate a strategic brief

```
/condition-brief heart failure
```

What happens: the skill fixes the segment, spawns five `information-gatherer` agents in
parallel, and writes `briefs/YYYY-MM-DD-<condition>.md`. Budget is roughly 20–30 searches.
Briefs are never overwritten — a second brief the same day gets a `-v2` suffix, and a later
brief stands alongside the earlier one so the delta is readable.

## 4. Deploy the dashboard

The staff-facing page is a published Artifact. It is already deployed for this
installation; the link is access-controlled and in the operator's hands, not in this repo.

To deploy your own copy, publish `condition-cards.html` (repository root) as an Artifact
with these runtime capabilities:

```json
{
  "sample": {},
  "user": { "scopes": ["profile"] },
  "db": { "rules": [
    { "path": "cards",    "read": "view",  "write": "admin" },
    { "path": "requests", "read": "view",  "write": "interact" },
    { "path": "drafts",   "read": "admin", "write": "admin" }
  ]}
}
```

Those three rules **are** the security model. Do not loosen them without reading §6.

## 5. Grant access

Share the dashboard from its Share menu. The access level decides the role, and getting
this wrong is the most common setup failure:

| Give them | They can | Who |
|---|---|---|
| **Contributor** | Read cleared cards, request a new card | Provider staff, front desk, MAs |
| **Editor** | All of the above, plus see the review queue and clear or return drafts | The clinician or pharmacist who reviews |
| Viewer | Read cleared cards only — **cannot request one** | Rarely what you want |

Viewers cannot write shared data under any rule, so a Viewer hits a dead end the first time
they ask for a card that does not exist yet. Default staff to **Contributor**.

## 6. The data model

Three collections, and the separation between them is the gate:

| Collection | Holds | Read | Write |
|---|---|---|---|
| `cards/<slug>` | Cleared cards, `status: "cleared"` | Everyone with access | Editors only |
| `drafts/<slug>` | Unreviewed cards + the fact-check report | **Editors only** | Editors only |
| `requests/<slug>` | The public status board | Everyone with access | Contributors and up |

Why it is built this way:

- Staff cannot read `drafts`, so unreviewed clinical content is **invisible**, not merely
  labelled as unreviewed. A label can be missed; an unreadable collection cannot.
- Staff cannot write `cards`, so no UI bug, no misconfiguration and no impatient user can
  put an uncleared card in front of a provider.
- `requests` exists so staff still see honest progress — *queued*, *research under way*,
  *with a reviewer*, *sent back* — without seeing the content.

### A limit worth stating plainly

The PHI screen is a safety net, not a guarantee. It strips names with titles, ages, dates,
phone numbers, record numbers and long identifiers before anything is sent or stored, and it
tells the user what it removed. It will not catch every shape of patient detail — a bare
name with no title and no number can get through. Train staff that the box takes a condition,
and treat the screen as the second line of defence rather than the first.

## 7. Put a card through the pipeline

1. A staff member searches a condition with no cleared card. A `requests/<slug>` document
   appears with `status: "queued"`.
2. The operator runs the pipeline for that condition: `information-gatherer` passes, then
   `cardbuilder`, then `factchecker`.
3. The draft is written to `drafts/<slug>` with `status: "pending_review"` and the
   fact-check report attached. Set `requests/<slug>.status` to `"in_review"` so staff see
   movement.
4. A reviewer opens the dashboard, works the review queue, and clears or returns it. See
   [REVIEWING.md](REVIEWING.md).
5. Clearing writes `cards/<slug>` with `status: "cleared"`. Every open dashboard updates on
   its own — nobody needs to reload.

## 8. Maintenance

- Cards flag as stale at **90 days**. Nothing re-runs automatically; staleness is surfaced,
  not fixed. Re-run the pipeline and send the new draft back through review.
- `cards/*.md` in the repo and the `cards` collection in the dashboard are separate copies.
  The repo holds the auditable artifact; the dashboard holds what staff read.

## 9. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Searched a condition, saw a pending state, no card | Correct behaviour — no cleared card exists | Run the pipeline, then review it |
| Staff member cannot request a card | They have Viewer access | Raise to Contributor |
| Reviewer sees no review queue | They are not an Editor, or no draft is pending | Raise to Editor; check `drafts` |
| "Clear for staff" is disabled | The fact-check returned a BLOCK verdict | Send it back; blocking defects cannot be cleared from the UI |
| Page says "Card store unavailable" | Viewer is signed out | Sign in; the store needs an identity |
| Card shows an as-of date months old | Expected; staleness is flagged at 90 days | Re-run the pipeline for that condition |
| A brief cites a guideline with no year | A gatherer failure that should have been caught | Reject it; "never cite a guideline without its year" is a hard rule |

## 10. What is not yet exercised

- No card has completed a full human review cycle in production.
- The dashboard opens on an **example card** that demonstrates layout only and is marked as
  such. The first cleared card replaces it.
- Staleness is flagged but nothing is scheduled to act on it.
