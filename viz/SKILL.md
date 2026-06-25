---
name: viz
description: Render a long structured answer — or any data worth visualizing — as a self-contained single-file scroll web page, by writing only thin YAML data (an ordered list of typed blocks) that a build script turns into DOM, big numbers, charts, SVG diagrams, trees, diffs, and layout. You never hand-write HTML or compute coordinates. Strongly prefer this whenever your reply would otherwise be a long expository read the user goes through start-to-finish (explaining how something works, an analysis or investigation writeup, comparing options or tradeoffs, a research/report summary, a codebase or architecture exploration, a multi-step plan, a status/metrics snapshot, a post-mortem) OR whenever the answer carries data with shape — metrics/big numbers, comparison tables, rankings, flow/architecture/sequence diagrams, file trees, code diffs, timelines — or a decision with options to put in front of the user and collect their pick. Also trigger on explicit asks — "visualize this", "diagram this", "show this as a page". Skip for short answers, code edits, commands, copy-pasteable text (commit messages, snippets), and headless/no-browser contexts.
---

# viz

Turn a long structured answer — or any data with shape — into a single self-contained
offline scroll web page the user opens and reads, by writing **only thin YAML data**: an
ordered list of typed blocks. `build.py` renders the DOM, SVG geometry, layout, and page
chrome from that data. You never hand-write HTML or compute coordinates — that is the whole
token/latency lever, and it is why the figures always come out correct.

## When to reach for it

Whenever the reply would be a long read the user goes through top-to-bottom, or whenever the
answer carries data with a shape worth seeing: magnitudes → big numbers, a ranking → bars,
options × criteria → a decision matrix, a branch/pipeline → a flowchart, a hierarchy or file
layout → a tree, a code change → a diff, events in order → a timeline, an interaction → a
sequence diagram, an open choice → selectable options. Skip it for short answers, code edits,
copy-paste snippets, and headless/no-browser contexts (fall back to markdown there).

## How to build one

1. **Outline the scroll** before any YAML: chunk the answer so each block carries one idea,
   and lead with the answer. This is where reading comfort is won.
2. **Get the vocabulary:** read `{{SKILL_DIR}}/schema.yaml`. It is the authoring reference —
   the page-level fields plus every block type, its fields, allowed values, and a worked
   example. Work from it directly; you do not need to open the component sources.
3. **Write ONLY the YAML** (a `title` + a `blocks:` list, optional `eyebrow`/`lead`/`skin`) to
   `/tmp/<slug>.yaml`. For each idea pick the block type whose shape matches the data and fill
   its fields. Do not emit HTML, CSS, or coordinates.
4. **Validate, then assemble:** `build.py --check --data <file>` reports precise located errors
   (typo'd type, missing/unknown field, bad enum); then
   `build.py --data <file> [--skin <name>] [--out <path>]`. Omit `--skin` for a random curated
   skin.
5. **Open** the output in the browser unless the user gave a location, and **leave a
   short pointer in chat** — what it covers and the path — not the full content. Re-dumping the
   answer defeats the purpose.

## Composition principles

- **Answer first, one idea per block.** Make headings and leads the takeaway ("Three forces
  drive the latency"), not a label ("Latency").
- **Let the data's shape pick the block** — don't default everything to prose. Match the
  construct to the data; each block's `desc` in `schema.yaml` says when it fits.
- **Comparable things in one block** — options/candidates go in a single table, `cards` row, or
  `compare`, never spread down the scroll.
- **Group related blocks; don't stack islands.** A flat run of full-width sections reads as a
  dump that leaves the column empty. Wrap blocks that form one unit in a `group` (optionally
  `columns: 2` for side-by-side, e.g. a table beside its notes), and lead with a tight overview
  cluster — earn density with structure, not by stretching blocks wider.
- **A decision → `decision` blocks:** selectable options that assemble into a copy-paste
  next-step prompt. Phrase each option's fragment in the user's own casual voice and language.
- **Pin a skin that fits the content.** Mono skins (`terminal-mono`) suit code/terminal
  walkthroughs; prose-heavy reports read better on an editorial skin (`newsprint`, `sage-press`,
  `warm-paper`). Omit to get a random curated one.
