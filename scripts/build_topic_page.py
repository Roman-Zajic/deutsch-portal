#!/usr/bin/env python3
"""Generate a grammar topic page from a spec, reusing the shared template.

Every topic page has identical chrome: navbar (logo | title | All topics | house),
three sections (concept, 20 worked examples, 100 translation exercises), the
German-letter keypad, the speaker button, the reveal/hide toggle, and the sticky
footer. Only the concept HTML, the examples and the data file differ, so the page
is built by substituting exactly a handful of blocks in the template document.

A spec is a JSON file:
{
  "slug": "konzessive-konnektoren",
  "title_en": "Concessive connectors",
  "title_de": "Die konzessiven Konnektoren",
  "store_key": "konzessive_konnektoren_progress_v1",
  "data_file": "grammar_exercises_konzessive_konnektoren.json",
  "concept_html": "  <!-- ══ 1. CONCEPT ══ -->\\n  <section> ... </section>",
  "examples": [["German — English", "why"], ...]        # exactly 20
}

Usage:  python3 build_topic_page.py spec.json [more.json ...]
Writes modules/grammar/<slug>.html.
"""
import json
import pathlib
import re
import sys

TEMPLATE = pathlib.Path("/opt/data/portal/modules/grammar/zweigliedrige-konjunktionen.html")
OUT_DIR = TEMPLATE.parent

# Anchors in the template, each spanning exactly the block we replace.
RE_TITLE = re.compile(r"<title>.*?</title>", re.S)
RE_H1 = re.compile(r"<h1>.*?</h1>", re.S)
RE_CONCEPT = re.compile(
    r"  <!-- ══ 1\. CONCEPT ══ -->.*?(?=  <!-- ══ 2\. EXAMPLES ══ -->)", re.S)
RE_EXAMPLES = re.compile(r"  var EXAMPLES = \[.*?\n  \];", re.S)
RE_FOOTER = re.compile(r'<footer class="footer">.*?</footer>', re.S)
RE_DATA_URL = re.compile(r'var DATA_URL = "[^"]*";')
RE_STORE = re.compile(r'var STORE = "[^"]*";')

# Strings from the template topic that must not survive into a new page.
TEMPLATE_LEAKS = (
    "Two-part connectors",
    "Two-part Connectors",
    "Die zweigliedrigen Konjunktionen",
    "grammar_exercises_zweigliedrig",
    "zweigliedrig_progress_v1",
)


def js_string(text):
    return text.replace("\\", "\\\\").replace('"', '\\"')


def build(spec):
    src = TEMPLATE.read_text(encoding="utf-8")

    out = RE_TITLE.sub(
        "<title>%s — %s | Deutsch Lernen</title>"
        % (spec["title_en"], spec["title_de"]), src, count=1)

    out = RE_H1.sub(
        '<h1>%s<span class="de">%s</span></h1>'
        % (spec["title_en"], spec["title_de"]), out, count=1)

    # The concept anchor runs up to the examples marker, so a spec that also
    # spells out section 2 would leave a duplicate behind. Drop it here.
    concept = spec["concept_html"]
    cut = concept.find("  <!-- ══ 2. EXAMPLES ══ -->")
    if cut != -1:
        concept = concept[:cut]
    concept = concept.rstrip() + "\n\n"
    out = RE_CONCEPT.sub(lambda m: concept, out, count=1)

    entries = ",\n    ".join(
        '["%s", "%s"]' % (js_string(a), js_string(b)) for a, b in spec["examples"])
    out = RE_EXAMPLES.sub("  var EXAMPLES = [\n    " + entries + "\n  ];", out, count=1)

    out = RE_DATA_URL.sub('var DATA_URL = "../../data/%s";' % spec["data_file"], out, count=1)
    out = RE_STORE.sub('var STORE = "%s";' % spec["store_key"], out, count=1)

    footer = ('<footer class="footer"><strong>%s</strong>'
              '<span class="footer-dot">·</span><span>Roman Zajic</span></footer>'
              % spec["title_en"])
    out = RE_FOOTER.sub(lambda m: footer, out, count=1)

    for leak in TEMPLATE_LEAKS:
        if leak in out:
            raise SystemExit("template leak: %r still present in the page" % leak)

    for anchor in ('id="examples"', 'id="quiz"', "var EXAMPLES", "var DATA_URL"):
        if anchor not in out:
            raise SystemExit("expected anchor missing: %s" % anchor)

    # Long German example sentences must never push a reference table wider than
    # the viewport on a phone. table-layout:fixed plus wrapping cells is the fix.
    if "table-layout:fixed" not in out:
        raise SystemExit("table overflow guard missing from the template CSS")
    if "overflow-wrap:anywhere" not in out:
        raise SystemExit("cell wrapping guard missing from the template CSS")

    return out


def main():
    specs = sys.argv[1:]
    if not specs:
        sys.stderr.write(__doc__)
        return 2

    for path in specs:
        spec = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        n = len(spec["examples"])
        if n != 20:
            raise SystemExit("%s: needs exactly 20 examples, has %d" % (path, n))
        target = OUT_DIR / (spec["slug"] + ".html")
        text = build(spec)
        target.write_text(text, encoding="utf-8")
        print("wrote %s (%d bytes)" % (target.name, target.stat().st_size))
    return 0


if __name__ == "__main__":
    sys.exit(main())