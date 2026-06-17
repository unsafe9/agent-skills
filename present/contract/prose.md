# present vocab · prose

Reading-document text & layout blocks. **Referenced by: scroll, slides.**

## Composing scroll

**Fragment:** `<main>` of `<section data-nav="…">` blocks, then a bottom `#composer` block.

Comprehension over spectacle; a sharp scannable document, not a marketing
landing page. The failure mode is a tall hero, giant type, and one idea spread
across each full screen — it spreads information thin. Open with a compact
`.hero` (a title block, not a full viewport), then a `.tldr`, then detail. The
real lever is grouping related data well (one comparison table/`.cards` row),
not squeezing — give the layout comfortable breathing room, neither cramped nor
sprawling. Keep headlines in the full-width container, never inside the narrow
`.prose` column (a big headline there wraps into a choppy stack).

| token | styled in | when to use | DOM shape |
|---|---|---|---|
| `.prose` | scroll | scroll reading column for body prose | `<div class="prose reveal">…</div>` |
| `.wide` | scroll, slides | wide column for a many-column table or a 4+ item card/stat row | `<div class="wide">…<table>…</table></div>` |
| `.hero`, `.title` | scroll (`.hero`), slides (`.title`) | opening header/title block | `<section class="hero">` / `<section class="slide title">` |
| `.tldr` | base, scroll | lead-with-the-answer box | `<div class="tldr"><p><strong>…</strong></p><p>…</p></div>` |
| `.band`, `.band--accent` | base | full-bleed tinted / accent section | `<section class="band">` or `<section class="band band--accent">` |
| `.split`, `.rev` | scroll | two things side by side (`.rev` swaps order) | `.split`: two direct children |
| `.cols`, `.col` | base (`.col h3`), prose, slides | two columns each with a sub-heading | two `<div class="col"><h3>…</h3>…</div>` |
| `.points` | base, scroll, slides | bulleted list, one claim per line | `<ul class="points"><li>claim<small>detail</small></li>…</ul>` |
| `.cards`, `.card` | base (`.card`), prose, scroll, slides | comparable items in ONE view | `<div class="cards"><div class="card"><h3>…</h3><p>…</p></div>…</div>` |
