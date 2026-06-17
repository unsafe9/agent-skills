# Mode: creative

The freeform escape hatch. The fast path (the default) wins on tokens and consistency by making you
write **only** a body fragment in a fixed vocabulary, which `build.py` assembles with a `base.css` +
skin + engine scaffold. Creative mode throws that scaffold away: you hand-author the whole page —
bespoke HTML, CSS, and inline SVG — art-directed for this one subject. You spend tokens and time to
buy a distinctive, expressive result the assembly path structurally cannot produce.

Reach for it only when the look IS the point: a portfolio-grade writeup, a landing-style explainer, a
deck whose visual identity matters as much as its content, or an explicit ask ("make it beautiful",
"design it properly", "make it premium", "like a landing page"). For an ordinary long answer, stay on the fast
path — it reads fine and costs a fraction.

## Art direction: defer to `frontend-design`

Do not re-derive design taste here. A `frontend-design` skill exists on this machine; load and apply
it as the design authority for this mode — its whole job is distinctive, intentional visual design
that does **not** read as a templated AI default. Borrow its full method: ground the design in the
subject, build a small token system (4–6 named colors, 2+ type roles, a layout concept, one signature
element), critique the plan against the generic-default looks before building, then spend your boldness
in one place and keep the rest disciplined. Everything that skill says about palette, typography,
structure-as-information, motion, restraint, and copy applies verbatim — read it there, don't restate
it.

If for some reason that skill is unavailable, the one rule that must survive is: **avoid the generic
AI aesthetic.** The three defaults to steer away from unless the brief explicitly asks for one — (1)
cream `#F4F1EA` + high-contrast serif + terracotta accent; (2) near-black + one acid-green/vermilion
accent; (3) broadsheet hairline rules with zero radius and dense columns. Make choices specific to the
subject instead.

## What creative KEEPS (non-negotiable, from `present` itself)

These are the `present` invariants the visual freedom does not buy out:

- **One self-contained file, fully offline.** No CDN, no external font/CSS/JS/image URL. Inline every
  asset: CSS in `<style>`, JS in `<script>`, images as `data:` URIs (base64), fonts as base64
  `@font-face` if a custom face truly earns it. The file must open with the network off.
- **Strong text/background contrast on every surface.** Expressive ≠ illegible. Check each colored
  band, scrim, and overlay — never low-contrast text on a busy or tinted fill. Keep visible keyboard
  focus and respect `prefers-reduced-motion`.
- **Nothing needs horizontal scrolling.** Size visuals to the column; give SVG a `viewBox` so it
  scales.
- **No GUI, no page.** In a headless/no-browser context, fall back to markdown — same as every mode.

## What creative RELAXES

- **The vocabulary manifest** (`contract.md`) — gone. Write whatever classes and structure the design
  needs. You are not emitting a body fragment for assembly; you are writing the document.
- **Skins** — gone. The token system you design IS the theme; there is no `base.css` + skin cascade to
  inherit or override.
- **IA rigidity.** The fast path's answer-first discipline (lead with a `.tldr`, force comparable
  things into one table/row) is a comprehension optimizer; here it becomes a **default you may break
  for expressive effect** — a slow reveal, a hero that withholds before it explains, a non-linear
  layout. Relax it on purpose, not by accident: the reader must still be able to follow and find the
  point. Don't bury the actual answer behind decoration.

## You may still inject an engine via `build.py`

Creative is freeform markup, but you don't have to re-implement page mechanics by hand. `build.py`
will wrap a hand-authored body in a chosen structure's shell + engine, so you can borrow, e.g., the
slides keyboard nav (`←/→/Space`, `O` overview, `N` notes) without writing the JS:

```
build.py --style slides --body <your-fragment> [--out path]
```

The catch: the shell's structural `<style>` and the engine assume their structure's DOM hooks
(`<section class="slide">`, `data-title`, `#deck`, `#overview`, the footer). If you inject an engine,
emit those hooks so the nav works, and let your bespoke CSS layer on top. If your design wants total
layout control, **skip `build.py` entirely** and write one standalone `.html` file by hand — that is
the purest creative path and still satisfies every KEEP above. Either way the output is a single
offline file (or a folder bundle when images are many/large — see `presentation.md`).

## Process

1. **Apply `frontend-design`'s plan-then-build loop.** Pin the subject, draft the token system,
   critique it against the generic defaults, revise, then build to the revised plan.
2. **Decide engine or standalone.** Want slides nav or overview? Author the structure's DOM hooks and
   run `build.py --style slides`. Want full control? Hand-write one file.
3. **Inline every asset** and verify offline (no `http(s)://`, no `<link>`, no external `src`).
4. **Self-critique the built page** for contrast on every surface, focus visibility, reduced-motion,
   and no horizontal scroll — then save to `/tmp/present-<slug>.html` (unless given a location), open
   it, and leave only a short pointer in chat.
