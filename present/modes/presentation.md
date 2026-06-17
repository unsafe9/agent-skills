# Mode: presentation

A deck a human will stand up and **deliver** to a room — not an answer to read alone at a screen. It
is a named flavor of **creative** mode with a fixed default and a thin overlay.

- **Inherits `creative`.** Read `{{SKILL_DIR}}/modes/creative.md` first and follow it: freeform
  art-directed HTML/CSS/SVG, the `frontend-design` skill as the design authority, and every KEEP
  (single offline file, no CDN, contrast on every surface, optional engine injection). The relaxations
  apply too — no fast-path vocabulary, no skins. This doc adds only what's specific to *presenting*; it
  does not restate creative.
- **Default STYLE = slides.** A presented deck is paginated and driven screen-by-screen, so inject the
  slides engine (`build.py --style slides`) to get `←/→/Space`, `O` overview, `N` notes for free —
  then layer the presentation art direction on top. (Hand-write a standalone file only if your design
  truly needs to escape the slides DOM.)

Use it when the user is deliberately making a presentation ("I'm going to present this", "make me a
proper deck", "make a deck I'll present"), not when they just want an answer shaped nicely. It trades the
most tokens and time of any path, so it is opt-in.

## The presentation overlay

What flips on top of creative when the deliverable is a *talk*:

- **Large type, read from a distance.** Size for the back row, not for a laptop. Headlines are big;
  body text is sparse and large. If a line can't be read across a room, it doesn't belong on the slide.
- **One idea + one focal visual per slide.** A presented slide is a backdrop for speech, not a
  document — a short headline and a single focal visual (chart, diagram, image, big number, or one
  sharp line). Minimal is not empty: the core point still has to land from the slide alone. A slide
  with no visual idea and no sharp line shouldn't exist. Push hard on SVG/CSS visualization; cut prose
  to the few words that must be *seen*.
- **The script is the real deliverable.** Whatever you'd otherwise put as on-slide text becomes the
  speaker script (below). Treat the notes as real writing, not an afterthought.
- **Higher craft, one art direction.** One palette, one type rhythm, aligned margins; a strong title
  and close; section-divider beats for chapters. Generated imagery shares one consistent brief.

### Narrative arc first

Find the spine before any slide: **hook → tension → resolution → ask.** What should the audience feel
and do by the end? Outline that arc, then map each beat to a single slide. Bookend the deck with a
cover open and a cover close that share the same art direction. Mark each chapter with a divider beat
so the spine is legible in the overview grid (`O`).

### Presentation layouts

Because creative is freeform you design these yourself, but a presented deck reliably needs three
imagery-forward beats on top of the ordinary content slides:

- **Cover / hero (open and close)** — a full-bleed image with a dark **scrim** gradient over it so
  white headline text stays legible from the back row. The scrim is non-negotiable: **never lay a
  headline straight on a bright image.** Generate the cover art wide/landscape. Reuse the same
  treatment to close, bookending the art direction.
- **Section divider** — a chapter break: a big chapter label (e.g. `01`) plus the chapter title with an
  accent treatment. One before each chapter; it resets the room's attention.
- **Captioned figure** — a generated illustration carrying the idea, with a one-line caption as the
  only on-slide text. The explanation is what you *say*, not what you write.

When you theme these, re-check contrast on every surface — the divider's accent-tinted band, the scrim
over a light image, colored stat numbers. Never light text on a light fill.

### Decisions are STATIC here

A room audience can't click. So a presented deck has **no interactive `#composer`** and no copy-out
prompt. Render a choice as a **discussion beat**: plain option cards, one marked as your recommendation
— but inert, not a button that assembles a prompt. Put the facilitation in the speaker notes: the
question to pose, who in the room gets the loudest vote, and a reminder to capture the answer yourself.

(The interactive decision + `#composer` loop belongs to the **fast** mode on the scroll/slides styles,
where the page is an answer the user reads and replies to. If you injected the slides engine, leaving
out the composer markup makes its composer JS harmlessly no-op.)

### Visualize on purpose

- **Branching flow → a deliberate inline SVG diagram** with real `<marker>` arrowheads and a `viewBox`
  so it scales to the column and never scrolls. Reserve a lightweight single-row node strip for a
  trivial pipeline. When a branch carries meaning (healthy vs. regressed), color its connector and
  arrowhead so the path reads at a glance.
- **Comparisons → a table with SHORT cells** — a word or phrase each. Many columns of sentence-length
  cells wrap into an unreadable stack; on a presented slide nobody reads a wrapped grid from across a
  room. Trim the cells, widen the table, or switch to one card per option.

## Speaker script (notes)

Every content slide gets an `<aside class="notes">` holding what the presenter says over it — the
narration, the transition to the next slide, a number to cite, a question to pose. With the slides
engine injected, `N` toggles notes (hidden by default, so the deck still reads clean without them).
Write spoken language, not bullets, and keep each note to what fits the time on the slide. This is the
deliverable the human leans on while presenting.

## Generated imagery

Use the available image-generation facility to create imagery that earns its place — a title hero, a
concept illustration, a metaphor, a section divider, a diagram too organic for SVG. Brief it for **one
consistent art direction** across the whole deck (palette, mood) matching the theme. Skip decorative
stock-feeling images; every image should carry meaning or set tone. For a full-bleed slide, generate
the image wide/landscape and lay the headline over a scrim.

Embedding — pick by image count and size:

- **Single file (default):** base64-encode each image and inline it as
  `<img src="data:image/...;base64,…">` (or as a CSS `background-image`). Keeps the one-file promise;
  fine for a handful. Watch total file size as images accumulate.
- **Folder bundle (many or large images):** save them beside the deck (e.g.
  `present-<slug>/assets/`) and reference them relatively. The deck is then a small folder — acceptable
  for a real presentation. Tell the user it's a folder, not a single file, when you hand it off.

## Process

1. **Find the narrative arc** — hook → tension → resolution → ask. Outline the spine before any slide.
2. **One idea per slide, mapped to a visual.** For each beat name the single visual and the headline;
   if you can't name the visual, the beat isn't ready. Bookend with a cover open + close; mark chapters
   with dividers.
3. **Generate the imagery** with a shared style brief (see above), then choose single-file vs folder.
4. **Write the script** into each slide's `<aside class="notes">`.
5. **Build** (default `build.py --style slides` for the nav, or standalone), inline assets, self-critique
   for contrast/scrim/focus/reduced-motion, save, and open.
6. **Hand off with how to present** — `N` shows notes, `O` overview, `←/→` to advance — and whether the
   deliverable is a single file or a folder.
