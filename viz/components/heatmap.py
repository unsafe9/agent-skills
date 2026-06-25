"""heatmap — a grid of cells shaded by intensity (one magnitude across two axes).

render(block) receives an already-validated block dict. Returns ONE complete
<section>…</section>. Each cell's numeric value is normalized across ALL cells to
0..1 and shaded with a single accent at varying strength (color-mix). Text flips to
--bg over strong cells so values stay legible on faint and strong cells alike."""
from _util import esc, section_open, section_close

# Past this normalized intensity, a cell's accent fill is strong enough that
# value text reads better as --bg (the page background) than --fg.
STRONG = 0.6


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _fmt(v) -> str:
    """Trim a trailing .0 so integers show as integers; keep other values as-is."""
    f = float(v)
    return str(int(f)) if f == int(f) else f"{f:g}"


def render(block: dict) -> str:
    cols = block["cols"]
    rows = block["rows"]
    unit = block.get("unit", "")
    usuffix = esc(unit) if unit else ""

    nums = [n for r in rows for n in (_num(c) for c in r["cells"]) if n is not None]
    lo = min(nums) if nums else 0.0
    hi = max(nums) if nums else 0.0
    span = hi - lo

    def cell(value) -> str:
        n = _num(value)
        if n is None:
            return '<div class="hm-cell hm-na" aria-hidden="true"></div>'
        frac = (n - lo) / span if span else 0.0
        pct = round(frac * 100)
        cls = "hm-cell hm-strong" if frac > STRONG else "hm-cell"
        style = f"background:color-mix(in srgb, var(--accent) {pct}%, var(--bg2))"
        return (f'<div class="{cls}" style="{style}">'
                f'<span class="hm-v">{esc(_fmt(n))}{usuffix}</span></div>')

    head = "".join(f'<div class="hm-col">{esc(c)}</div>' for c in cols)
    header = f'<div class="hm-corner" aria-hidden="true"></div>{head}'

    body = []
    for r in rows:
        cells = "".join(cell(c) for c in r["cells"])
        body.append(f'<div class="hm-rowlabel">{esc(r["label"])}</div>{cells}')

    grid_cols = f"--hm-cols:{len(cols)}"
    grid = (f'<div class="hm-grid" style="{grid_cols}">'
            + header + "".join(body) + "</div>")

    wrap = "wide" if len(cols) >= 6 else "wrap"
    return (section_open(block, cls="heatmap", wrap=wrap)
            + '<div class="hm-scroll">' + grid + "</div>"
            + section_close())
