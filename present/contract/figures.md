# present vocab · figures

Visual primitives — stats, charts, bar charts, diagrams, sequence/race, trees, layers. **Referenced by: scroll, slides, diagram.**

For the inline-SVG primitives (`.diagram`/`.swimlane`/`.race`/`.chart`), the `DOM shape` cell is a
sketch — copy the full SVG skeleton from a worked example; base.css only colors these, so it never
carries their geometry.

| token | styled in | when to use | DOM shape |
|---|---|---|---|
| `.stats`, `.stat`, `.n`, `.l`, `.good`, `.bad` | base, scroll, slides | big numbers (`.n` value + `.l` label; `.n` takes `.good`/`.bad`/`.accent`) | `<div class="stats"><div class="stat"><div class="n good">3.2×</div><div class="l">label</div></div>…</div>` |
| `.diagram`, `.dbox`, `.dt`, `.ds`, `.dconn` | base, figures | a flow with branches/fan-out (`.dbox` box, `.dt` title, `.ds` sub, `.dconn` connector) | inline `<svg class="diagram" viewBox="…">` with `.dbox`/`.dt`/`.ds`/`.dconn` + a `<marker>` arrowhead |
| `.flow`, `.node`, `.arrow` | base, scroll, slides | a TRIVIAL single-row pipeline only | `<div class="flow"><div class="node">…</div><span class="arrow">→</span>…</div>` |
| `.chart`, `.grid`, `.area`, `.line`, `.dot` | base, figures | inline SVG trend chart (sub-elements: gridlines/fill/stroke/points) | `<svg class="chart" viewBox="…">` with `.grid`/`.area`/`.line`/`.dot` |
| `.bars`, `.bar` | base, scroll, slides | pure-CSS bar chart (`.bar` holds `<i style="--v:%">`, `<b>`, `<span>`) | `<div class="bars"><div class="bar"><i style="--v:70%"></i><b>70</b><span>Tue</span></div>…</div>` |
| `.tree`, `.t-dir`, `.t-file` | base, figures | file/dir tree with CSS connector lines (replaces ad-hoc `<pre>` trees); long names wrap, never overflows | `<ul class="tree"><li><span class="t-dir">dir/</span><ul><li><span class="t-file">file</span></li></ul></li></ul>` |
| `.layers`, `.layer`, `.layer--accent` | base, figures | stacked abstraction layers (`.layer--accent` tints one); `<b>` label over a `<span>` note | `<div class="layers"><div class="layer"><b>UI</b><span>React</span></div><div class="layer layer--accent"><b>Domain</b><span>pure logic</span></div></div>` |
| `.swimlane` | base, figures | sequence diagram (inline SVG, viewBox): actors as columns, time downward, messages + activation bars | inline `<svg class="swimlane" viewBox="…">` with `.lane`/`.actor`/`.active`/`.msg`/`.msg--return`/`.mlabel` + a `<marker>` arrowhead |
| `.race` | base, figures | concurrency interleaving (inline SVG, viewBox): happens-before edges across lanes with a highlightable bad-interleaving `.race-window` (the headline capability) | inline `<svg class="race" viewBox="…">` with `.lane`/`.actor`/`.race-window`/`.evt`(`.ev`/`.evt-l`/`.lit` step state)/`.hb`(`.hb--cross`/`.hb--race`) + a `<marker>` |
