#!/usr/bin/env python3
"""Build a self-contained static front end.

The POC front end talks to the Express API. On a static host (S3, CloudFront, any object
store) those endpoints do not exist, so the page would load and then fail every call. This
inlines the data and swaps `api()` for a local resolver, producing ONE file with no
subresource fetches — which is also the only shape a single presigned URL can serve.

Output: dist/index.html
"""
import json, pathlib, re, sys, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "server" / "public" / "index.html"
OUT = ROOT / "dist" / "index.html"
CARDS = ROOT / "cards"
CATALOG = ROOT / "data" / "conditions.json"

SERVE_DEMO = "--cleared-only" not in sys.argv

html = SRC.read_text()
catalog = json.loads(CATALOG.read_text())

drafts = []
for f in sorted(CARDS.glob("*.json")):
    d = json.loads(f.read_text())
    d["slug"] = d.get("slug") or f.stem
    drafts.append(d)

if SERVE_DEMO:
    cards = [d for d in drafts if d.get("status") in ("cleared", "pending_review")]
    for c in cards:
        if c.get("status") != "cleared":
            c["demo"] = True
else:
    cards = [d for d in drafts if d.get("status") == "cleared"]

built = datetime.date.today().isoformat()

payload = {
    "builtAt": built,
    "demo": SERVE_DEMO,
    "static": True,
    "cards": cards,
    "drafts": drafts,
    "catalog": catalog,
}

# --- the local resolver: same call signature as api(), no network -------------------------
shim = """
<script>
/* Static build: the API is inlined. Same shapes the Express server returns, so the
   front-end code below is unchanged apart from api() routing here instead of to fetch. */
window.__HORIZON_STATIC__ = (function () {
  var D = __PAYLOAD__;
  function byKey() {
    var m = {};
    (D.catalog.conditions || []).forEach(function (c) {
      m[c.condition.toLowerCase()] = c; m[c.slug] = c;
      (c.aliases || []).forEach(function (a) { m[String(a).toLowerCase()] = c; });
    });
    return m;
  }
  var KEY = byKey();
  function resolve(q) {
    var k = String(q || "").toLowerCase().trim().replace(/\\s+/g, " ");
    if (KEY[k]) return KEY[k];
    var ks = k.replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
    if (KEY[ks]) return KEY[ks];
    if (k.length >= 4) {
      var hits = (D.catalog.conditions || []).filter(function (c) {
        return c.condition.toLowerCase().indexOf(k) === 0; });
      if (hits.length === 1) return hits[0];
    }
    return null;
  }
  function summary(c) {
    return { slug: c.slug, condition: c.condition, segment: c.segment, icd10: c.icd10,
             asOf: c.asOf, demo: !!c.demo, status: c.status,
             drugs: (c.drugs || []).length, news: (c.news || []).length };
  }
  function err(status, body) { var e = new Error("http " + status); e.status = status;
    e.body = body; throw e; }
  return {
    data: D,
    call: function (p) {
      var path = String(p).split("?")[0];
      var query = String(p).indexOf("?") > -1 ? String(p).split("?")[1] : "";
      if (path === "/healthz")
        return { ok: true, cards: D.cards.length,
                 catalog: (D.catalog.conditions || []).length, demo: D.demo,
                 "static": true, at: D.builtAt };
      if (path === "/api/catalog")
        return { count: (D.catalog.conditions || []).length, basis: D.catalog.basis,
                 tiers: D.catalog.tiers, conditions: D.catalog.conditions };
      if (path === "/api/cards")
        return { count: D.cards.length, cards: D.cards.map(summary) };
      if (path.indexOf("/api/cards/") === 0) {
        var slug = decodeURIComponent(path.slice("/api/cards/".length));
        var c = D.cards.filter(function (x) { return x.slug === slug; })[0];
        if (!c) err(404, { error: "no servable card for that slug" });
        return c;
      }
      if (path === "/api/drafts")
        return { count: D.drafts.length, drafts: D.drafts.map(function (d) {
          return { slug: d.slug, condition: d.condition, status: d.status, demo: !!d.demo,
                   verdict: (d.review && d.review.verdict) || null,
                   blocking: (d.review && (d.review.blocking || []).length) || 0,
                   fixes: (d.review && (d.review.fixes || []).length) || 0,
                   gaps: (d.notOnCard || []).length }; }) };
      if (path.indexOf("/api/drafts/") === 0) {
        var s2 = decodeURIComponent(path.slice("/api/drafts/".length));
        var d2 = D.drafts.filter(function (x) { return x.slug === s2; })[0];
        if (!d2) err(404, { error: "no such draft" });
        return d2;
      }
      if (path === "/api/resolve") {
        var m = /(?:^|&)q=([^&]*)/.exec(query);
        var hit = resolve(m ? decodeURIComponent(m[1].replace(/\\+/g, " ")) : "");
        if (!hit) err(404, { error: "not in catalog" });
        var has = D.cards.some(function (c) { return c.slug === hit.slug; });
        return Object.assign({}, hit, { hasCard: has });
      }
      if (path === "/api/requests")
        /* nothing to write to on a static host; the UI only needs this not to throw */
        return { status: "queued", persisted: false };
      err(404, { error: "not found" });
    }
  };
})();
</script>
"""

shim = shim.replace("__PAYLOAD__", json.dumps(payload, separators=(",", ":")))

# route api() through the shim when it is present
old_api = """  async function api(p, opts) {
    var r = await fetch(p, opts);
    if (!r.ok) throw Object.assign(new Error("http " + r.status), { status: r.status });
    return r.json();
  }"""
new_api = """  async function api(p, opts) {
    if (window.__HORIZON_STATIC__) return window.__HORIZON_STATIC__.call(p, opts);
    var r = await fetch(p, opts);
    if (!r.ok) throw Object.assign(new Error("http " + r.status), { status: r.status });
    return r.json();
  }"""
if old_api not in html:
    sys.exit("api() not found in source — the front end changed shape; update this script")
html = html.replace(old_api, new_api, 1)

# a static snapshot should say so, in the page
html = html.replace('<div class="note" id="envnote">loading</div>',
                    '<div class="note" id="envnote">static snapshot &middot; ' + built + '</div>', 1)
html = html.replace("<strong>Demonstration build.</strong>",
                    "<strong>Demonstration build &mdash; static snapshot of " + built
                    + ".</strong>", 1)

# the shim must be defined before the main script runs
html = html.replace("<script>\n(function () {", shim + "<script>\n(function () {", 1)

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(html)

kb = len(html.encode()) / 1024
print("dist/index.html  %.1f KB" % kb)
print("  cards inlined:   %d%s" % (len(cards), "" if SERVE_DEMO else " (cleared only)"))
print("  drafts inlined:  %d" % len(drafts))
print("  catalog entries: %d" % len(catalog.get("conditions", [])))
print("  subresource fetches: none — single file, presignable")
