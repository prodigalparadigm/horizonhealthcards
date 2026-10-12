# Where the knowledge base lives

Written for whoever asks this in a security or architecture review. Current as of 2026-10-12.

## Today: three locations, none production-grade

| What | Where it lives | Authoritative for |
|---|---|---|
| Cleared cards, drafts, card requests | The dashboard Artifact's own database, hosted by Anthropic. Three collections, 25,000-document cap | What staff and reviewers see right now |
| Card and brief source files | This git repository — `cards/*.md`, `cards/*.json`, `cards/*.review.md`, `briefs/` | The reviewable, auditable record |
| The 200-condition catalog | Two copies: `data/conditions.json`, and 200 static rows **inlined in `condition-cards.html`** | Input recognition and normalization |

## What that is not

**1. The system of record is on one machine.** `git remote` returns nothing. If that laptop
dies, the only surviving copy of the cards is inside a hosted artifact nobody has backed up.

**2. Access control is claude.ai identity, not the institution's.** Contributor and Editor on
an artifact are not entries in your IAM. No SSO, no group sync, and no automatic
deprovisioning when someone leaves — artifact shares are revoked by hand.

**3. No BAA, no SLA, no retention policy under your control.** None of these exist for this
deployment. A provider-facing clinical reference that is unavailable whenever claude.ai is
unavailable has no answer to "what do we do at 2am."

**4. The catalog is baked into the page.** Changing the 200 conditions means republishing
HTML, not editing data.

## The mitigating fact, and it is a real one

**There is no PHI in any of it, by design.** The dashboard screens patient identifiers out of
its input before anything is sent or stored, and the `requests` collection records only
condition names with no patient linkage. That makes the compliance conversation much shorter
than it would otherwise be. It does not make the conversation unnecessary, and "it is in a
Claude artifact" is not an answer to it.

## What production should look like

- **Repo as system of record.** Push to the institution's GitHub Enterprise or Azure DevOps.
  Cards become versioned files, and **the review gate maps onto pull-request approval** — which
  produces an audit trail carrying institutional identity rather than a field in a document.
- **Artifact as authoring and review workbench.** Where the pipeline runs and the reviewer
  works. Not the delivery surface.
- **Delivery on something your IT controls.** A static site or intranet page generated from
  the repo, behind your SSO. That is what providers hit, so nothing provider-facing depends on
  a vendor surface.

## Stopgap until a remote exists

Until the repo has a remote, take a bundle after each session and store it somewhere else:

```bash
git bundle create ~/backups/horizon-$(date +%Y%m%d).bundle --all
```

A bundle is a single file containing the full history; `git clone` restores from it directly.
This is a stopgap, not a backup strategy — it is manual, and it only protects what has been
committed.
