---
name: present
description: Render a long, structured answer as a self-contained single-file web page — opened in the browser and read there — instead of dumping it as a wall of markdown. Strongly prefer this whenever your reply would otherwise be a long expository response the user reads start-to-finish: explaining how something works, an analysis or investigation writeup, comparing options or tradeoffs, a research or report summary, a design or idea discussion, a codebase exploration, a multi-step plan, a status/metrics snapshot, a reference/cheatsheet, or a post-mortem. Especially reach for it whenever you need to put choices, options, or open questions in front of the user and collect their decision — present makes them selectable and copies back a next-step prompt. Choose a STYLE (scroll, slides, dashboard, cheatsheet, compare, diagram) for structure and a MODE (fast default, or creative/presentation) for craft. Also trigger on explicit asks — "present this", "slides", "deck", "dashboard", "cheatsheet", "show it as a web page", "break it into pages". Skip for short answers, code edits, commands, copy-pasteable text (commit messages, snippets), and headless/no-browser contexts.

---

# Present

Turn a long answer into a single self-contained HTML file the user opens and reads in the browser —
one idea at a time, at their own pace — instead of one scrolling wall of markdown. The goal is reading
comfort and visual clarity. It's web tech, so it's free to be a real web page, not a stack of PPT
rectangles. This is something to *read*, not an app: no controls or live editing.

## Route: pick a STYLE × a MODE

Every page is one **STYLE** (its structure) built in one **MODE** (how much craft you spend). Pick both,
then **follow that mode's doc** — this file only routes.

### STYLE — the structure (route by the answer's SHAPE)

| Style | Pick it for — and the boundary vs the neighbors |
|---|---|
| **scroll** (default) | a continuous top-to-bottom read: explanation, analysis, comparison, research, design discussion, code exploration. The catch-all — pick it unless a row below fits better. |
| **slides** | the same answer but *paginated*, advanced one screen at a time — when the parts are sequential beats, not a continuous read. Carries decisions + copy-out. |
| **dashboard** | a status/metrics snapshot seen at a glance — one screen, no scroll. NOT a read and NOT a decision surface (no options, no `#composer`). |
| **cheatsheet** | a dense reference/lookup card (commands, API, shortcuts), grouped by topic, print-friendly — scanned for one row, not read start-to-finish. |
| **compare** | a 2–5 candidate × criteria DECISION — Harvey-ball ratings + a radar (tradeoff shape) + a weighted scorecard. Pick over a scroll table when *choosing* is the point. Carries decision + copy-out. |
| **diagram** | ONE visual (architecture/sequence/concurrency) maximized to the viewport with a legend/step side rail. Pick only when the figure IS the answer — if a figure merely supports prose, drop the primitive inline in scroll instead. |

**Visuals are shared, not gated by STYLE.** The figure primitives — `.swimlane` (sequence), `.race`
(concurrency), `.diagram` (branching flow), `.chart`/`.bars`, `.tree`, `.layers`, plus
tables/`.stats`/`.cards` — drop inline into scroll and slides too. STYLE picks the page's overall shape
and chrome; it does NOT decide which visuals you may use. The `diagram` STYLE just hands ONE primitive
the whole viewport (the full-page canvas) — distinct from the `.diagram` class (one branching-SVG
primitive). So route by shape first, then compose with whatever visuals fit.

### MODE — the craft (read the doc before building)

| Mode | When | Read |
|---|---|---|
| **fast** (default) | almost everything — the token/latency lever. You write only a body fragment + skin pick; `build.py` assembles the page. Reads well, costs a fraction. | `{{SKILL_DIR}}/modes/fast.md` |
| **creative** | the look IS the point — a bespoke, art-directed page the assembly path can't produce. | `{{SKILL_DIR}}/modes/creative.md` |
| **presentation** | a deck a human will stand up and *deliver* (a named creative mode, default style = slides). | `{{SKILL_DIR}}/modes/presentation.md` |

Default to **scroll × fast**. Move to slides/dashboard/cheatsheet/compare/diagram when the answer's shape
calls for it or the user asks; move to creative/presentation only when craft is the explicit point.

## Principles (every STYLE and MODE)

- **Replace the markdown, leave a pointer.** The page *is* the answer; in chat give only a short pointer
  (what it covers + the path). Re-dumping the full answer defeats the purpose.
- **One idea per part; headlines are takeaways.** "Three forces drive the latency" beats "Latency."
- **Clarity over spectacle.** Lead with the answer; group related/comparable things so they're seen
  together (one table or row, not spread across sections). Lay it out with comfortable breathing room.
  Reserve dramatic treatment for the one thing that earns it.
- **Visualize, don't just list.** Comparisons → tables; magnitudes → big numbers; trends → inline SVG/CSS
  charts; sequences/architecture → boxes-and-arrows with a `viewBox` so they scale. Keep cells short and
  scannable; reserve bullets for list-shaped content.
- **Legible and on-screen.** Strong text/background contrast on every surface, especially colored bands.
  Nothing should need horizontal scrolling.
- **One self-contained file, offline.** No CDN anything.
- **No GUI, no page.** In a headless/no-browser context, fall back to markdown.

## Where to go next

- **Authoring a fast page** → run `python3 {{SKILL_DIR}}/build.py --guide --style <style>`. It prints
  the whole brief in one shot — the fragment to write, your STYLE's full vocabulary, worked examples to
  copy, the skins, and the build command. Work from that output; you don't need to open any other file.
- **The mode you picked** → `{{SKILL_DIR}}/modes/{fast,creative,presentation}.md`.
- **Assembly** → `{{SKILL_DIR}}/build.py` turns a STYLE + body fragment + skin into one offline file
  (`--check` lints a fragment, `--lint-skins` audits skins); skins live in `{{SKILL_DIR}}/skins/`.

Everything else — the assembled cascade, how the lint allowlist is derived, and how to add a STYLE or
skin — is documented where its own reader works: `contract.md` for the authoring contract, `build.py`
for the parser and extension steps.
