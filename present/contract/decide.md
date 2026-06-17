# present vocab · decide

Interactive decision + copy-out composer. **Referenced by: scroll, slides, compare.**

| token | styled in | when to use | DOM shape |
|---|---|---|---|
| `.decision` | base | a choice that needs the user's call (stacked groups self-space) | `<div class="decision" data-key="k"><div class="options">…</div></div>` |
| `.options`, `.option`, `.pick` | base, scroll, slides | the option grid (`.pick` marks your lean) | `<button class="option pick" data-frag="…">A · …<p>…</p></button>` |
| `.freeinput`, `.ask-input` | base, scroll, slides | optional free-text input | `<div class="freeinput"><label>…</label><textarea class="ask-input" data-key="k" data-frag="…: {v}"></textarea></div>` |
| `.ask` | base, scroll, slides | the "↓ pick and copy below" cue | `<p class="ask">…</p>` |
| `#composer`, `#prompt-preview`, `#copy-btn` | base, scroll, slides | assembles picks into a copyable next-step prompt (copy-confirm label defaults to `Copied ✓`; set `data-done` on `#copy-btn` to localize) | `<div id="composer" data-lead="…" data-tail="…"><pre id="prompt-preview"></pre><button id="copy-btn">…</button></div>` (scroll: wrap in `<div class="wrap">`) |
