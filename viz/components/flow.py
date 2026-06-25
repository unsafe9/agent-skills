"""flow — a branching flowchart. The model gives only nodes and edges; this
renderer COMPUTES the whole layout: it ranks nodes by longest-path from sources
(a topological layering), places ranks along `dir`, distributes nodes evenly in
each rank, sizes each box to fit its text, and routes every edge as a `.dconn`
bezier with a `<marker>` arrowhead. Cycles are broken so layering can't loop.

Coordinate geometry lives entirely here — that is the whole point of viz: the
model never emits SVG numbers. Classes (.diagram/.dbox/.dt/.ds/.dconn + the
marker) are lifted from present so flow.css can color them via skin tokens."""
from math import hypot
from _util import esc, section_open, section_close

# box / layout constants (SVG user units). Text-width estimates are CJK-aware and
# matched to the rendered font sizes (title 18px bold, sub 13px) so a box always
# contains its text — CJK/Hangul glyphs render ~1em wide, latin ~0.6em.
PAD_X = 16          # text inset inside a box
TITLE_LATIN = 11.0  # latin advance at the 18px bold title
TITLE_WIDE = 18.0   # full-width (CJK/Hangul) glyph at the title size
SUB_LATIN = 7.8     # latin advance at the 13px sub line
SUB_WIDE = 13.0     # full-width glyph at the sub size
MIN_W = 120
MAX_W = 320
BOX_H = 64          # box with a sub line
BOX_H_BARE = 48     # box with only a title
RANK_GAP = 96       # gap between rank bands (along flow axis)
CROSS_GAP = 26      # gap between siblings within a rank (cross axis)
MARGIN = 20         # viewBox margin


def _is_wide(ch):
    """Roughly full-width glyph (CJK, Hangul, fullwidth forms) — renders ~1em wide
    instead of a mono latin advance, so it needs more box width."""
    o = ord(ch)
    return (0x1100 <= o <= 0x115F or 0x2E80 <= o <= 0xA4CF
            or 0xAC00 <= o <= 0xD7A3 or 0xF900 <= o <= 0xFAFF
            or 0xFF00 <= o <= 0xFF60 or 0xFFE0 <= o <= 0xFFE6)


def _text_w(s, latin, wide):
    """Estimated rendered width of a string given per-glyph latin/wide advances."""
    return sum(wide if _is_wide(c) else latin for c in str(s))


def _parse_edges(raw_edges):
    """'a>b' or 'a>b: label' -> (src, dst, label|None). Trust validated shape."""
    out = []
    for e in raw_edges:
        s = str(e)
        label = None
        if ":" in s:
            s, label = s.split(":", 1)
            label = label.strip() or None
        if ">" not in s:
            continue  # malformed edge string — skip rather than crash
        src, dst = s.split(">", 1)
        out.append((src.strip(), dst.strip(), label))
    return out


def _rank_nodes(ids, edges):
    """Longest-path layering from sources. Edges that would point backward
    (cycles) are dropped for ranking so the longest-path loop terminates."""
    adj = {i: [] for i in ids}
    indeg = {i: 0 for i in ids}
    seen = set()
    acyclic = []
    for src, dst, _ in edges:
        if src not in adj or dst not in adj:
            continue
        if (src, dst) in seen:
            continue
        seen.add((src, dst))
        adj[src].append(dst)
        indeg[dst] += 1
        acyclic.append((src, dst))

    # Kahn topological order; nodes left in a cycle get appended after.
    from collections import deque
    order = []
    q = deque([i for i in ids if indeg[i] == 0])
    local_indeg = dict(indeg)
    while q:
        n = q.popleft()
        order.append(n)
        for m in adj[n]:
            local_indeg[m] -= 1
            if local_indeg[m] == 0:
                q.append(m)
    ranked_set = set(order)
    for i in ids:  # cycle remnant: append in declared order
        if i not in ranked_set:
            order.append(i)

    rank = {i: 0 for i in ids}
    for n in order:
        for m in adj[n]:
            if rank[m] < rank[n] + 1:
                rank[m] = rank[n] + 1
    return rank


def _box_size(node):
    title = str(node["title"])
    has_sub = bool(node.get("sub"))
    sub_w = _text_w(node.get("sub", ""), SUB_LATIN, SUB_WIDE) if has_sub else 0
    w = max(_text_w(title, TITLE_LATIN, TITLE_WIDE), sub_w) + PAD_X * 2
    w = max(MIN_W, min(MAX_W, w))
    h = BOX_H if has_sub else BOX_H_BARE
    return w, h


def render(block: dict) -> str:
    direction = block.get("dir", "auto")
    nodes = block["nodes"]
    by_id = {str(n["id"]): n for n in nodes}
    ids = [str(n["id"]) for n in nodes]
    edges = _parse_edges(block["edges"])

    rank = _rank_nodes(ids, edges)
    for n in nodes:                       # honor explicit rank overrides
        if n.get("rank") is not None:
            rank[str(n["id"])] = int(n["rank"])

    # auto orientation: a long chain reads better stacked vertically, a short one
    # fits horizontally. An explicit dir wins.
    if direction not in ("down", "right"):
        num_ranks = (max(rank.values()) + 1) if rank else 1
        direction = "down" if num_ranks >= 5 else "right"
    horizontal = direction == "right"

    # group node ids by rank, preserving declared order within a rank
    ranks = {}
    for i in ids:
        ranks.setdefault(rank[i], []).append(i)
    # apply optional in-rank `col` override (stable sort by col when given)
    for r, members in ranks.items():
        members.sort(key=lambda i: (by_id[i].get("col") is None,
                                    by_id[i].get("col", 0)))

    sizes = {i: _box_size(by_id[i]) for i in ids}

    # ---- place boxes ------------------------------------------------------
    # flow axis = the direction ranks advance; cross axis = within a rank.
    # For each rank, the band thickness (flow axis) is the max box extent.
    sorted_ranks = sorted(ranks)
    band_extent = {}   # rank -> max size along flow axis
    for r in sorted_ranks:
        if horizontal:
            band_extent[r] = max(sizes[i][0] for i in ranks[r])  # width
        else:
            band_extent[r] = max(sizes[i][1] for i in ranks[r])  # height

    # flow-axis origin per rank
    flow_pos = {}
    acc = MARGIN
    for r in sorted_ranks:
        flow_pos[r] = acc
        acc += band_extent[r] + RANK_GAP
    flow_total = acc - RANK_GAP + MARGIN

    # cross-axis span per rank, then center every rank on a shared midline
    cross_span = {}
    for r in sorted_ranks:
        members = ranks[r]
        if horizontal:
            s = sum(sizes[i][1] for i in members)  # heights
        else:
            s = sum(sizes[i][0] for i in members)  # widths
        cross_span[r] = s + CROSS_GAP * (len(members) - 1)
    cross_total = max(cross_span.values()) + MARGIN * 2
    midline = cross_total / 2

    pos = {}  # id -> (x, y) top-left
    for r in sorted_ranks:
        members = ranks[r]
        start = midline - cross_span[r] / 2
        cursor = start
        for i in members:
            w, h = sizes[i]
            if horizontal:
                x = flow_pos[r] + (band_extent[r] - w) / 2
                y = cursor
                cursor += h + CROSS_GAP
            else:
                x = cursor
                y = flow_pos[r] + (band_extent[r] - h) / 2
                cursor += w + CROSS_GAP
            pos[i] = (x, y)

    # ---- edge anchors -----------------------------------------------------
    # Each edge leaves a chosen SIDE of its src box and enters a chosen SIDE of
    # its dst box, picked from their relative rank/position: a forward edge uses
    # the facing sides, a backward edge the reverse sides, a same-rank edge the
    # cross-axis sides — so an edge never doubles back across its own box. Edges
    # sharing one side are fanned across it (ordered by the far endpoint) so
    # arrowheads don't pile on one point.
    def cross_center(i):
        x, y = pos[i]
        w, h = sizes[i]
        return (y + h / 2) if horizontal else (x + w / 2)

    def x_center(i):
        return pos[i][0] + sizes[i][0] / 2

    NORMAL = {"L": (-1, 0), "R": (1, 0), "T": (0, -1), "B": (0, 1)}

    def sides_for(src, dst):
        rs, rd = rank[src], rank[dst]
        if horizontal:
            if rd > rs:
                return "R", "L"
            if rd < rs:
                return "L", "R"
            return ("B", "T") if cross_center(dst) >= cross_center(src) else ("T", "B")
        if rd > rs:
            return "B", "T"
        if rd < rs:
            return "T", "B"
        return ("R", "L") if cross_center(dst) >= cross_center(src) else ("L", "R")

    valid = []
    edge_sides = {}
    side_groups = {}  # (node, side) -> [(k, far_node, is_src), ...]
    for k, (src, dst, _) in enumerate(edges):
        if src in pos and dst in pos:
            valid.append(k)
            ss, sd = sides_for(src, dst)
            edge_sides[k] = (ss, sd)
            side_groups.setdefault((src, ss), []).append((k, dst, True))
            side_groups.setdefault((dst, sd), []).append((k, src, False))

    frac = {}  # (k, is_src) -> fraction along the chosen side
    for (node, side), lst in side_groups.items():
        # fan along the side's free axis: vertical for L/R, horizontal for T/B
        lst.sort(key=lambda it: cross_center(it[1]) if side in "LR" else x_center(it[1]))
        n = len(lst)
        for s, (k, _far, is_src) in enumerate(lst):
            frac[(k, is_src)] = 0.5 if n == 1 else 0.26 + 0.48 * s / (n - 1)

    def anchor(i, side, f):
        x, y = pos[i]
        w, h = sizes[i]
        if side == "R":
            return (x + w, y + h * f)
        if side == "L":
            return (x, y + h * f)
        if side == "T":
            return (x + w * f, y)
        return (x + w * f, y + h)  # B

    def bez_mid(p0, c1, c2, p3):
        return (0.125 * p0[0] + 0.375 * c1[0] + 0.375 * c2[0] + 0.125 * p3[0],
                0.125 * p0[1] + 0.375 * c1[1] + 0.375 * c2[1] + 0.125 * p3[1])

    # ---- route edges ------------------------------------------------------
    # Short edges (<=1 rank apart) get a bezier that leaves and enters each box
    # perpendicular to its side. An edge spanning >=2 ranks is pushed into a side
    # lane outside the box column so it never crosses the boxes it skips over;
    # lanes stack outward, one per long edge per side. Labels ride each path's
    # own midpoint instead of piling up along the top.
    LANE_GAP = 30   # spacing between parallel lanes
    LANE_PAD = 22   # first lane's offset from the box column edge
    CORNER = 38     # lane entry/exit corner radius
    col_lo = min((pos[i][1] if horizontal else pos[i][0]) for i in ids)
    col_hi = max((pos[i][1] + sizes[i][1] if horizontal else pos[i][0] + sizes[i][0])
                 for i in ids)
    lane_lo, lane_hi = col_lo, col_hi
    left_n = right_n = 0

    routes = []  # (d, label, label_xy|None)
    for k in valid:
        src, dst, label = edges[k]
        ss, sd = edge_sides[k]
        sx, sy = anchor(src, ss, frac[(k, True)])
        ex, ey = anchor(dst, sd, frac[(k, False)])
        if abs(rank[dst] - rank[src]) >= 2:
            if cross_center(src) <= midline:
                lane = col_lo - LANE_PAD - left_n * LANE_GAP
                left_n += 1
                lane_lo = min(lane_lo, lane)
            else:
                lane = col_hi + LANE_PAD + right_n * LANE_GAP
                right_n += 1
                lane_hi = max(lane_hi, lane)
            if horizontal:
                sgn = 1 if ex >= sx else -1
                cr = min(CORNER, abs(ex - sx) / 2 - 1)
                d = (f'M{round(sx)} {round(sy)} '
                     f'C {round(sx + sgn*cr)} {round(sy)} {round(sx + sgn*cr)} {round(lane)} '
                     f'{round(sx + sgn*2*cr)} {round(lane)} L {round(ex - sgn*2*cr)} {round(lane)} '
                     f'C {round(ex - sgn*cr)} {round(lane)} {round(ex - sgn*cr)} {round(ey)} '
                     f'{round(ex)} {round(ey)}')
                lxy = ((sx + ex) / 2, lane + 4)
            else:
                sgn = 1 if ey >= sy else -1
                cr = min(CORNER, abs(ey - sy) / 2 - 1)
                d = (f'M{round(sx)} {round(sy)} '
                     f'C {round(sx)} {round(sy + sgn*cr)} {round(lane)} {round(sy + sgn*cr)} '
                     f'{round(lane)} {round(sy + sgn*2*cr)} L {round(lane)} {round(ey - sgn*2*cr)} '
                     f'C {round(lane)} {round(ey - sgn*cr)} {round(ex)} {round(ey - sgn*cr)} '
                     f'{round(ex)} {round(ey)}')
                lxy = (lane, (sy + ey) / 2 + 4)
        else:
            ns, nd = NORMAL[ss], NORMAL[sd]
            dist = max(30.0, 0.42 * hypot(ex - sx, ey - sy))
            c1 = (sx + ns[0] * dist, sy + ns[1] * dist)
            c2 = (ex + nd[0] * dist, ey + nd[1] * dist)
            d = (f'M{round(sx)} {round(sy)} C {round(c1[0])} {round(c1[1])}, '
                 f'{round(c2[0])} {round(c2[1])}, {round(ex)} {round(ey)}')
            lxy = bez_mid((sx, sy), c1, c2, (ex, ey))
        routes.append((d, label, lxy if label else None))

    # lanes can reach outside the box column — widen the cross axis and shift
    # everything so the leftmost/topmost lane still clears the margin.
    shift = max(0, MARGIN - lane_lo)
    cross_total = max(cross_total + shift, lane_hi + shift + MARGIN)
    vb_w = flow_total if horizontal else cross_total
    vb_h = cross_total if horizontal else flow_total
    gtx, gty = (0, shift) if horizontal else (shift, 0)

    # ---- emit -------------------------------------------------------------
    svg = [f'<svg class="diagram" viewBox="0 0 {round(vb_w)} {round(vb_h)}" '
           f'style="width:{round(vb_w)}px" role="img" aria-label="flowchart">',
           '<defs><marker id="vz-fa" viewBox="0 0 10 10" refX="9" refY="5" '
           'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
           '<path d="M0 0 L10 5 L0 10 z"/></marker></defs>',
           f'<g transform="translate({round(gtx)} {round(gty)})">']
    for i in ids:
        n = by_id[i]
        x, y = pos[i]
        w, h = sizes[i]
        cx = x + w / 2
        svg.append(f'<rect class="dbox" x="{round(x)}" y="{round(y)}" '
                   f'width="{round(w)}" height="{round(h)}" rx="10"/>')
        if n.get("sub"):
            svg.append(f'<text class="dt" x="{round(cx)}" y="{round(y + h/2 - 4)}">'
                       f'{esc(n["title"])}</text>')
            svg.append(f'<text class="ds" x="{round(cx)}" y="{round(y + h/2 + 15)}">'
                       f'{esc(n["sub"])}</text>')
        else:
            svg.append(f'<text class="dt" x="{round(cx)}" y="{round(y + h/2 + 6)}">'
                       f'{esc(n["title"])}</text>')

    for d, _label, _lxy in routes:
        svg.append(f'<path class="dconn" d="{d}" marker-end="url(#vz-fa)"/>')

    # labels go last so their chips sit over the lines; nudge any that would
    # overlap a label already placed (greedy vertical spread) so dense crossings
    # stay readable instead of stacking into one blob.
    placed = []  # (x0, x1, y) of laid-out label chips
    for _d, label, lxy in routes:
        if not label:
            continue
        mx, ty = lxy
        lw = len(str(label)) * 7 + 12
        x0, x1 = mx - lw / 2, mx + lw / 2
        bumped = True
        while bumped:
            bumped = False
            for px0, px1, py in placed:
                if x0 < px1 and x1 > px0 and abs(ty - py) < 18:
                    ty = py + 18
                    bumped = True
        placed.append((x0, x1, ty))
        svg.append(f'<rect class="dlabel-bg" x="{round(x0)}" '
                   f'y="{round(ty - 13)}" width="{round(lw)}" height="17" rx="4"/>')
        svg.append(f'<text class="dlabel" x="{round(mx)}" y="{round(ty)}">'
                   f'{esc(label)}</text>')

    svg.append('</g></svg>')
    return (section_open(block, wrap="wide")
            + '<div class="diagram-scroll">' + "".join(svg) + "</div>"
            + section_close())
