## viz — maintainer guide

`SKILL.md` tells an agent how to **use** viz to render a page. This file tells a
maintainer how to **change** viz — add or edit a block type, a skin, or the build.
Keep usage guidance in `SKILL.md` and modification guidance here, so a using agent
never loads it.

## Architecture in one breath

`build.py` validates a page's YAML against `schema.yaml`, renders each block to one
`<section>` through `components/<type>.py`, and concatenates the shell + CSS into one
offline HTML file. The model writes only `blocks:` data — never HTML, CSS, or
coordinates. The authoritative detail lives in the code; read it before changing it:

- `build.py` top docstring — the CSS cascade (base → skin → space → component →
  shell), the validation + coverage guard, the CLI.
- `schema.yaml` header — the field-spec vocabulary (`required`/`kind`/`enum`/`item`)
  and the page model.
- `components/_util.py` — the shared render helpers every component imports.

## Add (or change) a block type

A block type is exactly two coupled things, and `build.py`'s coverage guard fails the
build unless they match 1:1:

1. one entry under `blocks:` in `schema.yaml` (fields, enums, a worked `example:`),
2. a `components/<type>.py` exposing `render(block) -> str` (plus an optional
   `components/<type>.css`).

Steps:

1. Add the `schema.yaml` entry. The `desc` is what a using agent reads to pick the
   block — write it as "use this when…", and include a realistic `example:`.
2. Write `components/<type>.py`. Copy the shape of a close existing renderer —
   `components/stats.py` for field-driven markup, `components/compare.py` for
   hand-built SVG, `components/code.py` for a code frame.
3. If it needs styling, add `components/<type>.css`. It is tree-shaken in only when a
   block of that type appears on the page.
4. `python3 build.py --check --data <test.yaml>` must report PASS for both coverage
   and validation. Then build and eyeball it under a couple of skins
   (`--skin midnight`, `--skin newsprint`).

## The render() contract

`render(block: dict) -> str` returns ONE `<section>…</section>`.

- The block is already validated — trust it; read required fields directly, `.get()`
  optionals with a sane default.
- Import helpers from `_util`: `section_open(block, cls=, wrap=)` / `section_close()`
  bracket the section and wire the nav dot; `esc()` escapes every user-supplied
  string (raw f-string interpolation of user data is a bug); `embed_image(src, …)`
  inlines a local image as a data URI.
- `wrap` ∈ {`wrap`, `prose`, `wide`} picks the content width.
- Never crash the build on bad-but-valid data: coerce a non-numeric where a number is
  expected, guard divide-by-zero, degrade a missing file. One bad block must not take
  down the whole page.

## Container blocks (a block whose field holds other blocks)

A block type can nest a list of child blocks (see `group`). Three couplings must move
together:

- **Schema** — the child-list field is `kind: blocks`. `build.py`'s `_validate_block`
  recurses into it, dispatching each child by its own `type`.
- **Render** — the renderer calls `render_block` from `_util` per child and wraps the
  results. `build.py`'s `_collect_types` recurses into nested `blocks`, so a child type that
  appears *only* inside a container still gets its component CSS tree-shaken in.
- **CSS** — children render as ordinary `<section>`s; the container's CSS must strip their
  per-section chrome (block padding + centred width container) so the cluster reads as one
  unit instead of nested full-screen islands. See `components/group.css`.

## CSS rules (non-obvious, not enforced)

All component CSS is concatenated into one global stylesheet, so:

- **Scope every selector under the component's root class** (`.heatmap .hm-cell`, not
  a bare `.hm-cell`) or generic names leak across components.
- **Colors come only from skin tokens** — `var(--accent/--fg/--muted/--line/--bg/
  --bg2/--good/--bad/--code-bg)`, spacing from `var(--gap/--rhythm/--pad)`, and
  `var(--radius)`. Hardcoded hex won't reskin. `color-mix(in srgb, var(--token) N%, …)`
  is the token-safe way to vary intensity.
- A primitive emitted by a **shared helper** (e.g. `.img-missing` from `embed_image`,
  which both `image` and `bookmark` can produce) belongs in `base.css` (always
  loaded), not a component CSS (tree-shaken, so it would be missing whenever that one
  block type is absent).

## Offline invariant

The page must open with no network. `build.py` enforces it: external `@import`,
`url(http…)`, `<link>`, and remote `src` fail the build; `data:` URIs are allowed. Any
image is read from a local path and base64-inlined via `embed_image` — never reference
a remote URL as a resource.

## Skins

A skin is one `skins/<name>.css` that redefines the `:root` tokens and nothing
structural. Add the name to the `page.skin` enum in `schema.yaml` so it validates.
`build.py` picks a random skin when `--skin` is omitted.
