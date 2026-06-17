# present — assembly contract

Single source of truth for the FAST assembly path. At authoring time the model
outputs ONLY (1) a **body fragment** and (2) a **skin pick**. `build.py`
mechanically assembles a single self-contained offline HTML file from the shell,
`base.css`, the chosen skin, the engine, and the body. The CSS scaffold, JS
engine, and page chrome NEVER appear in model output — that is the token/latency
lever.

```
build.py --style {scroll|slides|dashboard|cheatsheet|compare|diagram} --body <fragment> [--skin <name>] [--seed N] [--out path]
```

Assembled cascade (final `<head>`):

1. `<style>{{CSS}}</style>` — `base.css`, THEN `skins/<name>.css`, THEN `space.css`
   (the shared elastic gap/pad ladder), THEN the `contract/<mod>.css` of each module
   this STYLE allowlists (base, skin, spacing scale, then module structural sizing).
2. `<style>` … shell structural CSS (literal in the shell, structure-specific) … `</style>`.

So: **base → skin → space → module-structural → shell-structural**. The skin's
`:root` overrides base tokens because it comes after; `space.css` then sets the
shared spacing ladder (`--gap*`/`--pad`/`--rhythm`, all `clamp()` so spacing is
elastic and consistent by construction); module and shell structural sizing come
after, so they win and are immune to reskinning (the shell loads last and can
override a module default — or rescale the whole spacing ladder in its own `:root`
— for its context).

build.py assembles a page from these parts under `{{SKILL_DIR}}`:
`{{SKILL_DIR}}/contract/<module>.md` (the per-capability vocabulary modules) and
their optional `{{SKILL_DIR}}/contract/<module>.css` (shared primitive sizing),
`{{SKILL_DIR}}/base.css`, `{{SKILL_DIR}}/skins/*.css`,
`{{SKILL_DIR}}/shells/<style>/shell.html`, `{{SKILL_DIR}}/shells/<style>/engine.js`,
`{{SKILL_DIR}}/shells/composer.js` (the shared decision/composer block), `{{SKILL_DIR}}/build.py`.

---

## 1. Vocabulary — load only your STYLE's modules

Your STYLE's vocabulary is the per-capability modules listed in
`{{SKILL_DIR}}/shells/<style>/modules` (`base` is always included). **Compose
only with their tokens; never reach outside them.** Each module holds the same four-column
table (`token`, `styled in`, `when to use`, `DOM shape`) for its slice of the
vocabulary, plus a `## Composing <style>` note — with the fragment that style must
provide — where one style owns it. Together a STYLE's modules are its **class
allowlist**. Page chrome (`#progress`, `nav.dots`, the slides footer wiring) is
shell-owned, never authored.

You may also use, without their own row: the sub-element classes shown inside a
parent's `DOM shape` cell (e.g. `.col`, `.n`/`.l`, `.sc-row`/`.sc-fill`); the
shell-chrome ids the engine wires up (`#progress`, `#bar`, `#counter`,
`#modeBtn`, `#deck`, `#overview`); and any `id` you name locally inside an
`<svg>` (e.g. a `<marker id="ah">` referenced by `marker-end="url(#ah)"`).

`--check` enforces that allowlist: it rejects any `class=` or `id=` outside your
STYLE's modules (plus the without-a-row extras above). The `styled in` column
names where each token is styled — `base` = `base.css`, a module name (e.g.
`figures`) = that module's `contract/<mod>.css` shared sizing, a shell name =
that shell's structural `<style>` — so every listed token resolves to a real
rule. Skins only decorate on top; modules and shells add structural sizing.

These tables double as `build.py`'s machine-readable lint source; keep the
four-column format intact when editing one, and see its `parse_module` for the
exact parsing rules.

## 2. Composition discipline

- **Answer-first.** Lead with the answer. Scroll: a `.tldr` near the top. Slides:
  state the takeaway as a full sentence on an early slide, not a label.
- **Comparable things in ONE view.** Options/approaches/candidates go in a single
  `table` or one row of `.cards` that compares at a glance — never spread across
  separate full-screen sections.
- **Match the construct to the data's shape** — don't default everything to prose
  or cards. Peer items → `.cards`; key→detail rows → a `table` or `.layers` (when
  there's a foundation/stack semantic); magnitudes → `.stats`; trend → `.chart`;
  ranking/distribution → `.bars`; sequence/branch/flow → an inline SVG
  (`.swimlane`/`.diagram`/`.flow`); hierarchy → `.tree`. Mind the count and width:
  4 peer items strand a 3-wide grid, so `.cards` balances 4 to 2×2 — but 5+ want a
  `.wide` container.
- **Diagram = inline SVG with a `viewBox`** so it scales and never scrolls. Use a
  real `<marker>` arrowhead and draw branches on purpose. `.flow` is ONLY for a
  trivial single-row pipeline; the moment it branches, switch to `.diagram`.
- **Keep table cells short** (a word/phrase). Many columns of sentence-length
  cells wrap into an unreadable stack — move nuance to a line below, or use
  `.cards` instead. `.wide` gives a many-column table room; `.nw` stops a short
  cell wrapping.
- **`#composer` at the bottom.** It assembles the user's picks into a short
  next-step prompt and copies it. Scroll: a fixed bottom composer section.
  Slides: the final slide.
- **Decision options each carry a `data-frag`**, marked `.pick` on your lean. The
  `#composer` reads `data-lead` / `data-frag` / `data-tail`; free-text inputs use
  `data-frag="…: {v}"`. Phrase all of these in the USER'S language and casual
  voice (how they talk to the AI) — keep them as the Korean fragments shown in
  the body samples unless the user writes in another language.

Per-style discipline lives in each module's `## Composing <style>` note, shown with
that module's vocabulary.

## 3. Skins

Skins are decoration-only GLOBAL themes; pick one by name with `--skin <name>` or omit
it for a random one. Authoring or auditing a skin (the invariants `build.py --lint-skins`
enforces) is documented for skin authors in `{{SKILL_DIR}}/skins/AUTHORING.md`.
