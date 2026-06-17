# present vocab · slides

Slide-deck chrome (slide unit, speaker notes, overview, footer controls). **Referenced by: slides.**

## Composing slides

**Fragment:** `<main id="deck">` of `<section class="slide" data-title="…">` blocks, then an `#overview` div and a `<footer>`.

One idea per slide, centered, sized large to read from a distance. Don't crowd a
screen; split into another slide. Every slide needs a `data-title` (it feeds the
counter + overview). The interactive decision goes on its own slide and the
`#composer` on the *next* slide so neither overflows.

| token | styled in | when to use | DOM shape |
|---|---|---|---|
| `.slide` | base, slides | one slide; `data-title` feeds counter + overview | `<section class="slide" data-title="Title"><div class="wrap">…</div></section>` |
| `.notes` | base, slides | speaker script, hidden until `n` | `<aside class="notes">…</aside>` inside a slide |
| `.ov-item`, `.ov-num`, `.ov-t` | base (`.ov-item`/`.ov-num`), slides | overview grid cells (engine-built from slide titles, never authored) | engine emits `<button class="ov-item"><span class="ov-num">N</span><span class="ov-t">…</span></button>` |
| `#overview` | slides | overview grid mount point (cells are `.ov-*`, filled by engine) | empty `<div id="overview"></div>` |
| `footer` | base, scroll, slides | page footer (scroll: read-cue strip; slides: fixed control bar) | scroll: shell-owned; slides: the literal footer block in the fragment |
| `.fbtn` | base, slides | slides footer control button (mode / overview) | `<button class="fbtn" id="modeBtn" onclick="toggleMode()">…</button>` |
