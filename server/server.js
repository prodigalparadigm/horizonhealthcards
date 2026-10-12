'use strict';
// Horizon condition cards - POC server.
// Serves the front end and a small read-mostly API over the card files in the repo.
// Deliberately has no database: cards are files, loaded at boot. See docs/BUILD-REPORT.md s7.

const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8080;          // App Runner sets PORT
const ROOT = path.resolve(__dirname, '..');
const CARDS_DIR = process.env.CARDS_DIR || path.join(ROOT, 'cards');
const CATALOG = process.env.CATALOG_FILE || path.join(ROOT, 'data', 'conditions.json');

// In a POC the demo cards are the point. In anything real this must be "cleared" only --
// reading the directory indiscriminately would publish blocked drafts.
const SERVE_DEMO = String(process.env.SERVE_DEMO || 'true') === 'true';

let cards = [];      // servable cards
let drafts = [];     // everything on disk, with review verdicts where present
let catalog = { conditions: [] };
let byKey = new Map();
const requests = []; // in-memory; a POC does not pretend to persist

function loadCatalog() {
  try {
    catalog = JSON.parse(fs.readFileSync(CATALOG, 'utf8'));
  } catch (e) {
    console.error('catalog unreadable:', e.message);
    catalog = { conditions: [] };
  }
  byKey = new Map();
  for (const c of catalog.conditions || []) {
    byKey.set(c.condition.toLowerCase(), c);
    byKey.set(c.slug, c);
    for (const a of c.aliases || []) byKey.set(String(a).toLowerCase(), c);
  }
}

function loadCards() {
  let files = [];
  try {
    files = fs.readdirSync(CARDS_DIR).filter(f => f.endsWith('.json'));
  } catch (e) {
    console.error('cards dir unreadable:', e.message);
  }
  const all = [];
  for (const f of files) {
    try {
      const d = JSON.parse(fs.readFileSync(path.join(CARDS_DIR, f), 'utf8'));
      d.slug = d.slug || f.replace(/\.json$/, '');
      all.push(d);
    } catch (e) {
      console.error('skipping unparseable card', f, e.message);
    }
  }
  drafts = all;
  cards = all.filter(d => d.status === 'cleared' || (SERVE_DEMO && d.status === 'pending_review'));
  // Anything served that was not actually cleared is flagged, so nothing reads as reviewed.
  for (const c of cards) if (c.status !== 'cleared') c.demo = true;
  console.log('loaded ' + cards.length + ' servable cards of ' + all.length + ' on disk'
              + (SERVE_DEMO ? ' (SERVE_DEMO=true - drafts included and flagged demo)' : ''));
}

function resolveCondition(text) {
  const k = String(text || '').toLowerCase().trim().replace(/\s+/g, ' ');
  if (byKey.has(k)) return byKey.get(k);
  const ks = k.replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
  if (byKey.has(ks)) return byKey.get(ks);
  if (k.length >= 4) {
    const hits = (catalog.conditions || []).filter(c => c.condition.toLowerCase().startsWith(k));
    if (hits.length === 1) return hits[0];
  }
  return null;
}

loadCatalog();
loadCards();

app.disable('x-powered-by');
app.use(express.json({ limit: '32kb' }));
app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('Referrer-Policy', 'no-referrer');
  next();
});

// App Runner probes this; keep it cheap.
app.get('/healthz', (_req, res) =>
  res.json({ ok: true, cards: cards.length, catalog: (catalog.conditions || []).length,
             demo: SERVE_DEMO, at: new Date().toISOString() }));

app.get('/api/catalog', (_req, res) =>
  res.json({ count: (catalog.conditions || []).length, basis: catalog.basis,
             tiers: catalog.tiers, conditions: catalog.conditions || [] }));

app.get('/api/cards', (_req, res) =>
  res.json({ count: cards.length, cards: cards.map(c => ({
    slug: c.slug, condition: c.condition, segment: c.segment, icd10: c.icd10,
    asOf: c.asOf, demo: !!c.demo, status: c.status,
    drugs: (c.drugs || []).length, news: (c.news || []).length })) }));

app.get('/api/cards/:slug', (req, res) => {
  const c = cards.find(x => x.slug === req.params.slug);
  if (!c) return res.status(404).json({ error: 'no servable card for that slug' });
  res.json(c);
});

// The review queue: drafts plus whatever verdict a fact-check attached.
app.get('/api/drafts', (_req, res) =>
  res.json({ count: drafts.length, drafts: drafts.map(d => ({
    slug: d.slug, condition: d.condition, status: d.status, demo: !!d.demo,
    verdict: (d.review && d.review.verdict) || null,
    blocking: (d.review && (d.review.blocking || []).length) || 0,
    fixes: (d.review && (d.review.fixes || []).length) || 0,
    gaps: (d.notOnCard || []).length })) }));

app.get('/api/drafts/:slug', (req, res) => {
  const d = drafts.find(x => x.slug === req.params.slug);
  if (!d) return res.status(404).json({ error: 'no such draft' });
  res.json(d);
});

app.get('/api/resolve', (req, res) => {
  const hit = resolveCondition(req.query.q);
  if (!hit) return res.status(404).json({ error: 'not in catalog', q: req.query.q || '' });
  const card = cards.find(c => c.slug === hit.slug);
  res.json(Object.assign({}, hit, { hasCard: !!card }));
});

app.post('/api/requests', (req, res) => {
  const cond = String((req.body && req.body.condition) || '').slice(0, 120);
  if (!cond) return res.status(400).json({ error: 'condition required' });
  const hit = resolveCondition(cond);
  const row = { condition: cond, slug: hit ? hit.slug : null,
                resolved: hit ? hit.condition : null,
                at: new Date().toISOString(), status: 'queued' };
  requests.push(row);
  if (requests.length > 500) requests.shift();
  res.status(201).json(row);
});

app.get('/api/requests', (_req, res) => res.json({ count: requests.length, requests }));

app.use(express.static(path.join(__dirname, 'public'), { extensions: ['html'] }));
app.use((_req, res) => res.status(404).json({ error: 'not found' }));

app.listen(PORT, '0.0.0.0', () =>
  console.log('horizon POC listening on ' + PORT + ' - health at /healthz'));
