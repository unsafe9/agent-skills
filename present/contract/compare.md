# present vocab · compare

Decision-matrix vocabulary (candidates × criteria, Harvey-balls, radar, scorecard). **Referenced by: compare.**

## Composing compare

**Fragment:** `<main class="matrix" style="--cands:N">` of a `.cmp-head`, a `.cmp-grid`, an optional `.cmp-panels` row, and a bottom `#composer`.

A decision matrix, not a feature wall: candidates across the top (`.cand`, your
lean `.cand--lead`), criteria down the gutter (`.crit`), one `.cell` per
intersection in candidate order. Each cell leads with a `.cell-top` (a `.rate`
Harvey-ball + a `.verdict` chip) so the per-criterion winner scans by pattern
before any prose; `.heat`/`.win` tint and ring the strong cells, nuance goes in
the cell's `<p>`, never a paragraph in the gutter. Back the grid with the
`.cmp-panels` pair — a `.radar` (the tradeoff SHAPE a table can't show) beside a
`.scored` weighted scorecard (the ranked verdict) — then close on a `.crit--pick`
row of per-column `.option`s feeding the `#composer`. It IS a decision surface:
keep the decision + copy-out loop (unlike dashboard).

| token | styled in | when to use | DOM shape |
|---|---|---|---|
| `.matrix` | compare | compare-style root: a candidates × criteria decision matrix (`--cands:N` declares the candidate count) | `<main class="matrix" style="--cands:3"><header class="cmp-head">…</header><div class="cmp-grid">…</div><div id="composer">…</div></main>` |
| `.cmp-head` | compare | compare header block (question + `.lead` framing line) | `<header class="cmp-head"><h1>Which queue?</h1><p class="lead">3 candidates against 5 criteria.</p></header>` |
| `.cmp-grid`, `.cmp-corner` | compare | the matrix grid: flat children in source order (`.cmp-corner` is the top-left blank, sticky on both axes) | `<div class="cmp-grid"><div class="cmp-corner"></div>…</div>` |
| `.cand`, `.cand--lead`, `.cand-sub` | compare | sticky candidate column header (`.cand--lead` marks your lean, `.cand-sub` is the one-line descriptor; clicking a header dims the other columns) | `<div class="cand cand--lead"><h2>SQS</h2><p class="cand-sub">managed</p></div>` |
| `.crit`, `.crit--pick` | compare | sticky criterion gutter label (one per row; an optional `.wt` badge shows the scorecard weight; `.crit--pick` labels the final pick row) | `<div class="crit">Operational cost<span class="wt">weight ×3</span></div>` … `<div class="crit crit--pick">Pick</div>` |
| `.cell`, `.cell--pick`, `.cmp-dim` | compare | one matrix cell in candidate order; lead with a `.cell-top` row (Harvey-ball `.rate` + `.verdict` chip) so the criterion scans by pattern, then a `<p>` note. Add `.heat` to tint the cell by its score and `.win` to ring the row winner. `.cell--pick` wraps a column's pick `.option`; `.cmp-dim` is the engine-added off-column dim | `<div class="cell heat good win" style="--v:.95"><div class="cell-top"><span class="rate good" style="--v:.95"></span><span class="verdict good">Lowest</span></div><p>note…</p></div>` … `<div class="cell cell--pick"><button class="option pick" data-frag="Go with SQS">Choose SQS</button></div>` |
| `.verdict` | base, compare | cell judgement chip; takes `.good`/`.warn`/`.bad` for color | `<span class="verdict good">Lowest</span>` |
| `.rate` | base, compare | Harvey-ball rating — ONE circle whose fill fraction (`--v`:0..1) encodes a score so the reader scans the per-criterion winner by pattern; takes `.good`/`.warn`/`.bad` to color the fill by direction | `<span class="rate good" style="--v:.9"></span>` |
| `.cmp-panels`, `.cmp-panel` | compare | the companion panel row under the matrix: the radar (tradeoff shape) beside the scorecard (ranked verdict). Each `.cmp-panel` has an `<h2>` + `.sub` caption | `<section class="cmp-panels"><div class="cmp-panel"><h2>Tradeoff shape</h2><span class="sub">…</span><svg class="radar">…</svg></div><div class="cmp-panel"><h2>Weighted score</h2>…<div class="scored">…</div></div></section>` |
| `.radar` | base, compare | radar/spider overlay (inline SVG, viewBox): each candidate's strength/weakness profile as a filled polygon over a shared criterion web — a tradeoff SHAPE a table cannot show | `<svg class="radar" viewBox="…">` with `.web`/`.spoke`/`.axis-l`/`.blob`(`.b`/`.c` recolor per candidate)/`.blob-dot` |
| `.scored` | base, compare | weighted scorecard: authored per-criterion weights drive a computed total per candidate; the ranked winner row gets `.win`, dominated candidates `.out` (static, `--v`:0..1 sets each bar width) | `<div class="scored"><div class="sc-row win" style="--v:1"><span class="sc-name"><b>SQS</b><span>8.6 / 10</span></span><span class="sc-track"><i class="sc-fill"></i></span><span class="sc-total">8.6</span></div><div class="sc-row out" style="--v:.42"><span class="sc-name"><b>Redis</b><span>dominated</span></span><span class="sc-track"><i class="sc-fill"></i></span><span class="sc-total">3.8</span></div><p class="sc-foot">weights: cost ×3 · throughput ×2 …</p></div>` |
