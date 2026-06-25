"""compare — a weighted decision matrix. Criteria are rows, candidates columns;
each rating (0–4) renders as an SVG Harvey ball (0=empty … 4=full). A weighted
total row sums rating×weight per candidate and highlights the winner. With
`radar: true` an inline radar SVG overlays each candidate's ratings across the
criteria web.

Geometry — the Harvey-ball wedges and the radar polygon points — is computed
here from the data. Classes are lifted from present (.rate via an SVG analogue,
.radar/.web/.spoke/.axis-l/.blob/.scored) so compare.css colors via skin tokens."""
import math

from _util import esc, section_open, section_close

# radar geometry
R_CX, R_CY, R_R = 170, 160, 120
R_VB_W, R_VB_H = 340, 320
RINGS = 4
BALL_R = 11   # Harvey-ball radius (SVG user units)
BLOB_CLASSES = ["", "b", "c"]  # accent, good, bad — recolored per candidate


def _ball(value):
    """0–4 fill as a small inline SVG: empty ring → quarter wedges → full disc."""
    frac = max(0, min(4, int(value))) / 4.0
    r = BALL_R
    parts = [f'<svg class="hball" viewBox="0 0 {2*r+4} {2*r+4}" width="{2*r+4}" '
             f'height="{2*r+4}" aria-hidden="true">',
             f'<circle class="hb-ring" cx="{r+2}" cy="{r+2}" r="{r}"/>']
    if frac >= 1.0:
        parts.append(f'<circle class="hb-fill" cx="{r+2}" cy="{r+2}" r="{r}"/>')
    elif frac > 0:
        # wedge from 12 o'clock clockwise spanning frac of the circle
        ang = 2 * math.pi * frac
        ex = r + 2 + r * math.sin(ang)
        ey = r + 2 - r * math.cos(ang)
        large = 1 if frac > 0.5 else 0
        d = (f'M{r+2} {r+2} L{r+2} {2} '
             f'A{r} {r} 0 {large} 1 {ex:.2f} {ey:.2f} Z')
        parts.append(f'<path class="hb-fill" d="{d}"/>')
    parts.append('</svg>')
    return "".join(parts)


def _radar(candidates, criteria):
    """Each candidate's ratings as a filled polygon over a shared criterion web.
    Axis k points from center at angle (top = -90deg), radius = rating/4 * R."""
    m = len(criteria)
    if m < 3:
        return ""  # radar needs at least a triangle to read as a shape
    angles = [(-math.pi / 2) + (2 * math.pi * k / m) for k in range(m)]

    def point(k, frac):
        return (R_CX + R_R * frac * math.cos(angles[k]),
                R_CY + R_R * frac * math.sin(angles[k]))

    svg = [f'<svg class="radar" viewBox="0 0 {R_VB_W} {R_VB_H}" role="img" '
           'aria-label="radar of candidates over criteria">']
    # concentric web rings
    for ring in range(1, RINGS + 1):
        frac = ring / RINGS
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in
                       (point(k, frac) for k in range(m)))
        svg.append(f'<polygon class="web" points="{pts}"/>')
    # spokes
    for k in range(m):
        x, y = point(k, 1.0)
        svg.append(f'<line class="spoke" x1="{R_CX}" y1="{R_CY}" '
                   f'x2="{x:.1f}" y2="{y:.1f}"/>')
    # one blob per candidate
    for ci in range(len(candidates)):
        cls = BLOB_CLASSES[ci % len(BLOB_CLASSES)]
        pts = []
        for k, crit in enumerate(criteria):
            ratings = crit["ratings"]
            v = ratings[ci] if ci < len(ratings) else 0
            frac = max(0, min(4, int(v))) / 4.0
            x, y = point(k, frac if frac > 0 else 0.001)
            pts.append(f"{x:.1f},{y:.1f}")
        svg.append(f'<polygon class="blob {cls}" points="{" ".join(pts)}"/>')
    # axis labels just outside each spoke
    for k, crit in enumerate(criteria):
        lx = R_CX + (R_R + 14) * math.cos(angles[k])
        ly = R_CY + (R_R + 14) * math.sin(angles[k])
        anchor = "middle"
        if math.cos(angles[k]) > 0.3:
            anchor = "start"
        elif math.cos(angles[k]) < -0.3:
            anchor = "end"
        svg.append(f'<text class="axis-l" x="{lx:.1f}" y="{ly:.1f}" '
                   f'text-anchor="{anchor}">{esc(crit["name"])}</text>')
    svg.append('</svg>')
    return "".join(svg)


def render(block: dict) -> str:
    candidates = [str(c) for c in block["candidates"]]
    criteria = block["criteria"]
    nc = len(candidates)

    # weighted totals per candidate
    totals = [0.0] * nc
    max_possible = 0.0
    for crit in criteria:
        w = float(crit.get("weight", 1))
        max_possible += w * 4
        ratings = crit["ratings"]
        for ci in range(nc):
            v = ratings[ci] if ci < len(ratings) else 0
            totals[ci] += w * max(0, min(4, int(v)))
    win = max(range(nc), key=lambda i: totals[i]) if nc else None

    # ---- matrix table -----------------------------------------------------
    rows = ['<thead><tr><th class="crit-h">criterion</th>']
    for ci, c in enumerate(candidates):
        wcls = ' class="win"' if ci == win else ""
        rows.append(f'<th{wcls}>{esc(c)}</th>')
    rows.append('</tr></thead><tbody>')
    for crit in criteria:
        w = crit.get("weight", 1)
        ratings = crit["ratings"]
        wt = f'<span class="wt">×{esc(w)}</span>' if str(w) not in ("1", "1.0") else ""
        rows.append(f'<tr><th class="crit">{esc(crit["name"])}{wt}</th>')
        for ci in range(nc):
            v = ratings[ci] if ci < len(ratings) else 0
            wincls = ' class="win"' if ci == win else ""
            rows.append(f'<td{wincls}>{_ball(v)}</td>')
        rows.append('</tr>')
    # weighted total row
    rows.append('<tr class="total"><th class="crit">weighted total</th>')
    for ci in range(nc):
        t = totals[ci]
        tstr = f"{t:.0f}" if t == int(t) else f"{t:.1f}"
        wincls = ' class="win"' if ci == win else ""
        crown = ' <span class="crown">★</span>' if ci == win else ""
        rows.append(f'<td{wincls}><b>{tstr}</b>{crown}</td>')
    rows.append('</tr></tbody>')
    table = (f'<table class="cmp-matrix" style="--cands:{nc}">'
             + "".join(rows) + '</table>')

    out = [table]

    # ---- optional radar ---------------------------------------------------
    if block.get("radar"):
        radar = _radar(candidates, criteria)
        if radar:
            legend = ['<div class="legend">']
            swatches = ["a", "b", "bad"]
            for ci, c in enumerate(candidates):
                sw = swatches[ci % len(swatches)]
                legend.append(f'<span><span class="swatch {sw}"></span>{esc(c)}</span>')
            legend.append('</div>')
            out.append('<div class="cmp-radar">' + radar + "".join(legend) + '</div>')

    return (section_open(block, wrap="wide")
            + "".join(out)
            + section_close())
