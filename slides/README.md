# The executive deck

Five slides. Source of truth is `deck.json` (order, sections, typefaces) plus one HTML file
per slide under `slides/`, in the Slides artifact format — a single `<section>` on a fixed
1920x1080 canvas with inline styles only, plus an `<aside>` of speaker notes.

## Rebuilding demo_deck.pdf

`print.html` assembles all five slides into one printable document with the typefaces
embedded from `fonts/`, and strips the speaker notes. Regenerate with:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-pdf-header-footer --allow-file-access-from-files \
  --virtual-time-budget=20000 --run-all-compositor-stages-before-draw \
  --print-to-pdf=demo_deck.pdf "file://$PWD/slides/print.html"
```

The fonts are committed deliberately. Headless Chrome does not reliably fetch Google Fonts
during a print run, and the first build of this PDF silently fell back to Arial on every
slide — the deck's whole typographic treatment was lost and the file still looked plausible.
Verify after any rebuild:

```bash
python3 -c "import re;d=open('demo_deck.pdf','rb').read();\
print(sorted(set(re.findall(rb'/BaseFont\s*/([A-Za-z0-9+\-,]+)',d))))"
```

Expect IBMPlexSans and SourceSerif4 subsets. If you see only ArialMT, the fonts did not load.

Speaker notes live in each slide's `<aside>` and are not in the PDF — read them in the
artifact, or in the slide files.
