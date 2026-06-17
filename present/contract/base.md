# present vocab · base

Cross-cutting essentials — bare HTML elements, colour states, and chrome shared by every style. **Always loaded.**

| token | styled in | when to use | DOM shape |
|---|---|---|---|
| `main` | scroll, slides | body wrapper | scroll: `<main>` of `<section data-nav="…">`; slides: `<main id="deck">` of `<section class="slide" data-title="…">` |
| `.wrap` | scroll, slides | default content column (width is structural) | `<div class="wrap">…</div>` |
| `.reveal`, `.in` | scroll | fade-in on scroll enter (`.in` added by engine) | add `.reveal` to a section's inner `<div>` |
| `.eyebrow`, `.kicker` | base, scroll (`.eyebrow`), slides (`.kicker`) | small accent label above a heading | `<div class="eyebrow">Topic · context</div>` |
| `h1`, `h2`, `h3` | scroll, slides | title / section heading / sub-heading | plain heading element |
| `p`, `.lead` | base (`.lead` color), scroll, slides | body text / larger framing line | `<p>…</p>` / `<p class="lead">…</p>` |
| `table`, `.nw`, `.yes`, `.no` | base | several options × dimensions, in ONE view (`.nw` no-wrap; `.yes`/`.no` color a cell) | `<table>…<td class="yes nw">…</td>…</table>` |
| `.table-scroll` | base | horizontal scroll wrapper for an over-wide table | `<div class="table-scroll"><table>…</table></div>` |
| `.quote`, `blockquote` | base | a single quotable line | scroll: `<p class="quote">…<cite>…</cite></p>`; slides: `<blockquote>…<cite>…</cite></blockquote>` |
| `pre`, `code`, `.cmt`, `.key`, `.str` | base, scroll, slides | a short code snippet (`.cmt`/`.key`/`.str` tint spans) | `<pre><code>…<span class="key">…</span>…</code></pre>` |
| `.accent` | base | inline accent-colored text span | `<span class="accent">…</span>` |
| `.hint` | slides, cheatsheet | slides footer keymap hint / cheatsheet one-line note under a row | `<span class="hint">M mode · O overview · N notes · ← →</span>` / `<p class="hint">terse note</p>` |
| `.dot` | dashboard | three-state status dot (`.good`/`.warn`/`.bad`) | `<span class="dot good"></span>` |
| `.warn` | dashboard | warn/degraded state color (on `.dot`/`.pill`/a table cell) | `<span class="dot warn"></span>` / `<td class="warn">…</td>` |
| `.legend` | base, dashboard, diagram | a flex row of color-keyed items (the flex row + `<span>` items are styled in base; dashboard places it in the footer as a status-dot legend, diagram places it in the side rail as a `.swatch` key) | dashboard: `<div class="legend"><span><span class="dot good"></span>Healthy</span>…</div>`; diagram: `<div class="legend"><span><span class="swatch a"></span>Actor A</span>…</div>` |
| `.swatch`, `.a`, `.b`, `.bad` | base, diagram | a small color-keyed chip inside a `.legend` (`.a` accent, `.b` good/second actor, `.bad` danger) | `<span class="swatch a"></span>` / `<span class="swatch bad"></span>` |
