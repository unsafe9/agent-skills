# present vocab · canvas

Figure-first canvas chrome (stage, caption, annotation rail, steps). **Referenced by: diagram.**

## Composing diagram

**Fragment:** `<main class="canvas">` of a `.fig-head`, one or more `.stage` figures, and an optional `.annot` side rail.

A figure-first canvas: ONE visual is the content, text is the supporting
scaffold. NOT billboard-narrative (that's slides) and NOT a pan/zoom app —
"read, not an app". Lead with a `.fig-head` (an `.eyebrow` over a one-line `h1`
takeaway), give the `.stage` the focal inline-SVG primitive
(`.swimlane`/`.race`/`.diagram`/`.chart`) sized to fill, and put the one-line
result in a `<figcaption>`. An optional `.annot` side rail carries a numbered
`.steps` walk-through (each `<li data-step="k">` lights the matching SVG group)
and/or a `.legend`; the rail scrolls internally so the figure never does. Every
SVG uses a `viewBox` so it scales to fit with no horizontal scroll. The `diagram`
STYLE is the full-page canvas; `.diagram` (the class) is just one of the
primitives that can fill it — don't conflate them. The shared primitives
(`.tree`/`.layers`/`.swimlane`/`.race`) are structure-neutral and drop inline
into scroll/slides too; the STYLE only hands one the whole viewport.

| token | styled in | when to use | DOM shape |
|---|---|---|---|
| `.canvas` | diagram | diagram-STYLE root: a figure-first frame that maximizes ONE inline-SVG visual; gains a side rail when an `.annot` is present | `<main class="canvas"><header class="fig-head">…</header><figure class="stage">…</figure><aside class="annot">…</aside></main>` |
| `.fig-head` | diagram | diagram header block (`.eyebrow` over an `h1` takeaway) | `<header class="fig-head"><div class="eyebrow">Topic · context</div><h1>The one-line claim</h1></header>` |
| `.stage` | diagram | holds the ONE focal SVG (`.swimlane`/`.race`/`.diagram`/`.chart`) maximized to fill, plus a `<figcaption>`; repeat to stack figures | `<figure class="stage"><svg class="race" viewBox="…">…</svg><figcaption>one-line takeaway</figcaption></figure>` |
| `figcaption` | diagram | one-line takeaway under the focal figure | `<figcaption>Without the mutex one increment vanishes.</figcaption>` |
| `.annot` | diagram | diagram side rail: a numbered `.steps` list and/or a `.legend`; scrolls internally so the SVG never does | `<aside class="annot"><ol class="steps">…</ol><div class="legend">…</div></aside>` |
| `.steps` | diagram | numbered step list; each `<li data-step="k">` (`.on` when active, `.bad` marks a failure step) lights the SVG group carrying the matching `data-step` | `<ol class="steps"><li data-step="1"><b>T1 reads n=0</b><span>before T2 wrote</span></li><li data-step="3" class="bad"><b>both write n=1</b><span>one increment lost</span></li></ol>` |
