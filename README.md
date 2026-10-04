# Deutsch Lernen

A learning portal for German, built as static pages and served by GitHub Pages.

## Structure

- `index.html` — portal home, lists every module
- `modules/<name>/index.html` — one directory per module

## Adding a module

1. Create `modules/<name>/index.html`
2. Add an entry to the `MODULES` array in `index.html` with `status: "live"`
3. Commit — GitHub Pages rebuilds automatically

Set `status: "soon"` to have the card render as locked without linking anywhere.
