# present

Render a long, structured answer as a self-contained single-file web page —
opened in the browser and read there — instead of dumping it as a wall of
markdown. Pick a STYLE (scroll, slides, dashboard, cheatsheet, compare, diagram)
for structure and a MODE (fast default, or creative/presentation) for craft;
`build.py` assembles the shell + base CSS + skin + body fragment into one offline
HTML file with no CDN dependencies.

## Prerequisites

- **Programs**: Python 3 (standard library only — no `pip install`) to run
  `build.py`.
- **Services / auth**: none.
- **Environment**: a desktop browser to open and read the generated page. In a
  headless / no-browser context the skill falls back to plain markdown.

## Usage

```bash
# Print the full authoring brief for a STYLE (fragment shape, vocabulary,
# worked examples, skins, build command) in one shot:
python3 build.py --guide --style scroll

# Assemble a page from a body fragment + skin pick:
python3 build.py --style scroll --body body.html --out page.html
```

See `SKILL.md` for routing (STYLE × MODE) and `modes/{fast,creative,presentation}.md`
for the craft path you picked.
