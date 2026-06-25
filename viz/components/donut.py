"""donut — proportions as a ring of arcs. Each item's value is summed into a
whole; its share drives one arc of a single SVG ring drawn with the standard
stroke-dasharray / stroke-dashoffset technique (a transparent-fill circle whose
visible stroke segment spans share×circumference). Arcs are laid head-to-tail
from 12 o'clock so they exactly close the full circle. `center` text sits in the
hole. A legend lists each label with its share %, raw value, and a swatch that
matches its slice.

Geometry (radius, circumference, per-arc offsets) is computed here so model
output stays thin. Colors come only from skin tokens: a slice honors its `tone`
(good/bad/accent), and untoned slices cycle a small palette derived from
var(--accent)/var(--muted) via color-mix — donut.css owns the actual values."""
from _util import esc, section_open, section_close

R = 60          # ring radius in SVG user units
STROKE = 30     # ring thickness
VB = 160        # viewBox is VB×VB; ring centered at VB/2
CIRC = 2 * 3.141592653589793 * R

TONE_VARS = {"good": "var(--good)", "bad": "var(--bad)", "accent": "var(--accent)"}
# untoned slices cycle these palette slots (defined in donut.css)
PALETTE = ["p0", "p1", "p2", "p3", "p4"]


def _num(v) -> float:
    """Coerce a slice value to float; a non-numeric value counts as 0 rather than
    crashing the whole build (the validator does not enforce numeric types)."""
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _shares(items):
    """Largest-remainder rounding so the displayed integer %s sum to exactly 100
    (avoids 99/101 artifacts). Returns the float share and the rounded int %."""
    nums = [_num(it["value"]) for it in items]
    total = sum(nums)
    if total <= 0:
        n = len(items)
        return [(1.0 / n, round(100 / n)) for _ in items] if n else []
    fracs = [n / total for n in nums]
    floors = [int(f * 100) for f in fracs]
    remainder = 100 - sum(floors)
    order = sorted(range(len(items)), key=lambda i: (fracs[i] * 100 - floors[i]),
                   reverse=True)
    pcts = floors[:]
    for k in range(remainder):
        pcts[order[k]] += 1
    return list(zip(fracs, pcts))


def _color(item, palette_idx):
    tone = item.get("tone")
    if tone in TONE_VARS:
        return TONE_VARS[tone], None
    return None, PALETTE[palette_idx % len(PALETTE)]


def render(block: dict) -> str:
    items = block["items"]
    shares = _shares(items)
    cx = cy = VB / 2

    arcs = []
    legend = []
    offset = 0.0          # running fraction of the circle already consumed
    palette_idx = 0
    for it, (frac, pct) in zip(items, shares):
        color, pclass = _color(it, palette_idx)
        if pclass is not None:
            palette_idx += 1
        seg_cls = f"seg {pclass}" if pclass else "seg"
        style = f' style="--seg:{color}"' if color else ""
        seg_len = frac * CIRC
        # dasharray draws one visible run of seg_len then a gap of the remainder;
        # dashoffset rotates the run's start to the head of the previous arc.
        dash_off = -offset * CIRC
        arcs.append(
            f'<circle class="{seg_cls}"{style} cx="{cx:.1f}" cy="{cy:.1f}" '
            f'r="{R}" fill="none" stroke-width="{STROKE}" '
            f'stroke-dasharray="{seg_len:.3f} {CIRC - seg_len:.3f}" '
            f'stroke-dashoffset="{dash_off:.3f}"/>')
        offset += frac

        sw_style = f' style="--seg:{color}"' if color else ""
        sw_cls = f"sw {pclass}" if pclass else "sw"
        legend.append(
            '<li class="row">'
            f'<span class="{sw_cls}"{sw_style}></span>'
            f'<span class="lab">{esc(it["label"])}</span>'
            f'<span class="pct">{pct}%</span>'
            f'<span class="val">{esc(it["value"])}</span>'
            '</li>')

    center = block.get("center")
    hole = (f'<div class="hole"><span>{esc(center)}</span></div>'
            if center else "")

    ring = (
        '<div class="ring">'
        f'<svg class="donut-svg" viewBox="0 0 {VB} {VB}" role="img" '
        'aria-label="proportion donut chart">'
        # track behind the arcs so a sub-100% sum still reads as a full ring
        f'<circle class="track" cx="{cx:.1f}" cy="{cy:.1f}" r="{R}" '
        f'fill="none" stroke-width="{STROKE}"/>'
        + "".join(arcs)
        + '</svg>'
        + hole
        + '</div>')

    body = (
        '<div class="donut">'
        + ring
        + '<ul class="donut-legend">' + "".join(legend) + '</ul>'
        + '</div>')

    return section_open(block) + body + section_close()
