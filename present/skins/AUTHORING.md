# Authoring a present skin

A skin is a **GLOBAL theme**: one `skins/<name>.css` that works on every STYLE. After
adding or editing one, run `build.py --lint-skins` — it audits contrast and structural
leaks across all skins. (Page authors never read this; they just pick a skin by name, or
omit `--skin` for a random one.)

- **Skins are GLOBAL.** One skin file works on every structure. This holds because a
  skin is scoped to exactly what transfers across structures.
- **A skin OWNS:** `:root` tokens (palette colors, `--font`/`--mono`/optional `--serif`,
  `--radius`) and DECORATIVE vocabulary styling (surface fills, borders, shadows, accent
  treatments, interaction states, serif/italic assignment) via structure-agnostic
  selectors.
- **A skin must NEVER own structural sizing:** no type scale (`h1`/`h2`/`h3`/`p`/`.lead`
  font-size), no container widths (`--maxw`/`--prose`/`--pad`), no `section`/`.slide`
  spacing rhythm, no mode positioning (`mode-slides`/`mode-scroll`), no nav chrome
  positioning (`nav.dots`/`footer`/`#progress`/`#overview`/`.ov-*`), no `.reveal`. Those
  live in the shell and are immune to reskinning. This is exactly why scroll reads
  document-grade and slides reads billboard-grade from the SAME skin file.
- **Every surface passes contrast.** Dark text on light fills (or vice versa) on every
  surface, including any accent band. A light skin must override the base accent band
  (which is dark-text-on-bright-accent) to a treatment that keeps legible contrast —
  e.g. a pale wash with dark text, not inverted text.
- **Offline only.** A skin must introduce no external resource — no `@import url(http…)`,
  web font, or remote asset. (`build.py` asserts the assembled page has no `{{…}}` left
  and no `http(s)://` / `<link` / external `src=`; the output is one offline file.)
