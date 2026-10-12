# Presenter quickstart — the executive slide

One slide. Five minutes of talking if they are interested, ninety seconds if they are not.
Read this once before you walk in.

## The slide in one sentence

One condition request produces two different products for two different readers, and
neither reaches anyone before an independent check that can block it.

## The three cards, in order

**Left — the strategy brief.** Six sections, every claim carries its source, and a mandatory
"could not confirm" section so the team knows the brief's edges rather than guessing at
them. This is what you read before a capital, service-line or drug-spend decision.

**Middle — the provider card.** One page, read in ninety seconds between patients. Condition,
quick summary, what changed recently, and the current drug resources. Boxed warnings are not
optional: a card that lists an agent without its boxed warning is treated as defective and
will not clear.

**Right — the gate. Spend your time here.** This is the part that distinguishes the system
from a chatbot pointed at a search engine, and the part a cautious executive actually cares
about. The fact-checker opens every cited source rather than trusting that a real-looking
link says what the card claims. It can block. And the enforcement is structural rather than
procedural: staff accounts physically cannot write a card, so an unreviewed card cannot
reach a provider even if someone wants it to.

## Before you present

Fill the two bracketed numbers in the bottom band — `[__ conditions]` and
`[__ service lines]`. They are deliberately blank; do not improvise them on stage.

Know the current status, and say it plainly: the pipeline, the agents, the dashboard and the
review queue are built. Ask what has cleared review so far before you claim a number.

## Questions you will get

**"Can it just generate a card on demand?"**
No, deliberately. Live generation would be uncited model recall, which is exactly what the
gate exists to prevent. The dashboard serves cards that already cleared review and queues
the rest. If that sounds like a limitation, it is the opposite — it is the control.

**"Is this clinical decision support?"**
No. It is an informational reference assembled from FDA labeling and published society
guidelines, and it says so on the page and on this slide. It does not recommend treatment
for an individual patient, and the card never says "give X" — it says what the label or the
guideline says, attributed.

**"What stops it making something up?"**
Three things, in order of strength. The card builder has no web access at all, so it can
only assemble what was gathered. The fact-checker independently opens the cited sources and
can block. And the data layer restricts who can publish a card, so the gate is not something
a person can skip under time pressure.

**"Who is accountable for what a provider reads?"**
A named human reviewer clears every card, and the clearance is recorded with their name and
the date on the card itself.

**"What about patient privacy? It is a free-text box in a clinic."**
It screens patient details out of the input before anything is sent or stored, and tells the
user plainly that cards cover conditions, not patients. That was designed in, not added
after, because a free-text box in a provider's office receives patient information routinely.

**"How current is it?"**
Every card carries a visible as-of date, and cards flag themselves stale at ninety days.
Nothing is silently old.

**"What does it cost to run?"**
Roughly 20–30 searches per condition, plus review time. Be straight that review time is the
real constraint, not compute.

## What not to claim

- Do not say it is validated, certified, or cleared by anyone. It is not.
- Do not say it replaces clinical judgment or a drug reference. It does not.
- Do not quote coverage or volume numbers you have not confirmed.
- Do not describe the example card on the dashboard as a real card. It demonstrates layout.

## If you only get one line

"It turns a condition name into decision-ready intelligence for two audiences, and nothing
reaches a clinician until a named human has cleared it against the sources."
