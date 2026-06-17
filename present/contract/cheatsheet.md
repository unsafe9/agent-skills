# present vocab · cheatsheet

Reference-card blocks (page, groups, defs, cmds, keys). **Referenced by: cheatsheet.**

## Composing cheatsheet

**Fragment:** `<main class="page">` (a compact header + `.scope`, the `.sheet`, a `<footer>`).

A dense reference card, scanned not read: the reader wants one row fast. No hero,
no TL;DR — a compact header states the scope and gets out of the way. Group by
topic (`.group`, most-used first) with short concrete headings; each group is
kept whole by `break-inside:avoid`, so split a huge topic into two groups rather
than one tall card. Density is organized, not crammed: short cells and short
rows, `.nw` to stop a mid-token wrap, nuance pushed to a `.hint` under the
group — never into a cell. Mono `<code>` for commands/flags, `<kbd>` key-caps for
keys.

| token | styled in | when to use | DOM shape |
|---|---|---|---|
| `.page` | cheatsheet | cheatsheet outer column container | `<main class="page"><header>…</header><div class="sheet">…</div><footer>…</footer></main>` |
| `.scope` | cheatsheet | one-line scope under the cheatsheet title | `<p class="scope">covers <b>…</b></p>` |
| `.sheet` | cheatsheet | the multi-column flow that pours groups down columns | `<div class="sheet"><section class="group">…</section>…</div>` |
| `.group` | cheatsheet | one topic card (never splits across a column/page) | `<section class="group"><h2>Topic</h2>…</section>` |
| `.defs` | cheatsheet | definition rows (term → meaning) — for SHORT terms; a long or mono command belongs in `.cmds` | `<dl class="defs"><div><dt>Term</dt><dd>meaning</dd></div>…</dl>` |
| `.cmds` | cheatsheet | command rows (a mono command stacked over its note) — use for ANY long/mono command so it survives a narrow column | `<ul class="cmds"><li><code>cmd</code><span>note</span></li>…</ul>` |
| `.keys` | cheatsheet | keyboard-shortcut rows (`.combo` groups `<kbd>` caps, `.sep` joins a chord, `.act` is the action) | `<ul class="keys"><li><span class="combo"><kbd>⌘</kbd><kbd>S</kbd></span><span class="act">Save</span></li><li><span class="combo"><kbd>g</kbd><span class="sep">then</span><kbd>g</kbd></span><span class="act">Go to top</span></li>…</ul>` |
