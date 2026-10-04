# Deutsch Lernen

A German learning portal — static pages served by GitHub Pages. No build step, no dependencies.

## Structure

```
index.html                     portal home; MODULES registry lives here
modules/<name>/index.html      one directory per module
data/<name>.json               module data, stored in this repo
```

## Data

Module data is plain JSON committed to this repository.

- `data/vocabulary.json` — the vocabulary word list

Because the repository is public, modules **read** their data anonymously over
`raw.githubusercontent.com`. **Writing** back needs the user's own token, entered
in the module's save dialog and kept in that browser's `localStorage` only.

A token is never committed to this repository or embedded in any page.

## Adding a module

1. Create `modules/<name>/index.html`
2. Add its data file under `data/`
3. Register it in the `MODULES` array in `index.html` with `status: "live"`
4. Commit — Pages rebuilds automatically

`status: "soon"` renders the card locked, with no link.
