# present vocab · dashboard

Status-board tiles (head, KPIs, panels, status table, sparkline, footer). **Referenced by: dashboard.**

## Composing dashboard

**Fragment:** the `.head` strip + sections directly — the shell provides the grid wrapper, so no `<main>`.

A single-viewport, no-scroll status board: the whole picture in one frame. NOT a
reading document and NOT a decision surface (no selectable options or
`#composer`). Lead with a `.head` strip (board title + as-of / status pill), then
3–5 `.kpi` tiles (the few numbers that matter, delta color carrying direction),
then one status table and/or one mini-chart, then a `.legend` + source stamp.
**If it doesn't fit, cut or group tiles — never add scrolling.** Status dots are
three-state and filled (`.dot.good/.warn/.bad`), high-contrast — a bad row must
be unmistakable.

| token | styled in | when to use | DOM shape |
|---|---|---|---|
| `.head` | dashboard | dashboard header strip (board title + as-of/context) | `<header class="head"><h1>…</h1><div class="ctx"><span>as of <b>…</b></span><span class="pill good">…</span></div></header>` |
| `.pill` | dashboard | dashboard status chip (`.good`/`.warn`/`.bad`) | `<span class="pill warn"><span class="dot warn"></span>Degraded</span>` |
| `.kpis` | dashboard | dashboard KPI tile strip (3–5 big numbers) | `<section class="kpis"><div class="panel kpi"><div class="v">128<small>k/s</small></div><div class="l">label</div><div class="d up">▲ 6%</div></div>…</section>` |
| `.panel` | dashboard | dashboard tile/card surface (fills its grid cell) | `<div class="panel"><div class="ph"><h2>…</h2><span class="sub">…</span></div>…</div>` |
| `.kpi` | dashboard | a single KPI tile (`.v` value, `.l` label, `.d` delta with `.up`/`.down`/`.flat` — SENTIMENT, not arrow direction: `.up`=good/green, `.down`=bad/red, `.flat`=muted, so a rising error rate or latency is `.down`) | `<div class="panel kpi"><div class="v">214<small>ms</small></div><div class="l">p99</div><div class="d down">▲ 18ms</div></div>`; flat variant `<div class="d flat">— steady</div>` |
| `.grid2` | dashboard | dashboard main body split (table + chart) | `<section class="grid2"><div class="panel">…</div><div class="panel">…</div></section>` |
| `.ph` | dashboard | dashboard panel header (`.sub` = right-aligned sub-label) | `<div class="ph"><h2>Regional status</h2><span class="sub">4 regions</span></div>` |
| `.tblwrap` | dashboard | clipping wrapper around the status table (no scroll) | `<div class="tblwrap"><table>…<td class="num">…</td><td class="nw">…</td>…</table></div>` |
| `.chartbox` | dashboard | dashboard mini-chart holder (`.scale` = axis labels under it) | `<div class="chartbox"><svg class="spark" …>…</svg><div class="scale"><span>…</span><span>…</span></div></div>` |
| `.spark` | dashboard | inline SVG sparkline, viewBox-scaled to fill the panel (`.area`/`.line`/`.grid`) | `<svg class="spark" viewBox="0 0 100 40" preserveAspectRatio="none"><line class="grid"/><path class="area"/><path class="line"/></svg>` |
| `.foot` | dashboard | dashboard footer (status legend + source stamp) | `<footer class="foot"><div class="legend"><span><span class="dot good"></span>Healthy</span>…</div><div>source…</div></footer>` |
