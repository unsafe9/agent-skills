"""sequence — a sequence diagram. Actors become evenly-spaced columns with a
dashed lifeline running down; each message is an arrow from sender to receiver
at the next time row, label above it, plus an activation bar on the receiver.
`return: true` draws a dashed return arrow in the muted color.

All coordinates are computed here from actor count × message count. Classes
(.swimlane/.lane/.actor/.active/.msg/.msg--return/.mlabel + the marker) are
lifted from present so sequence.css colors them via skin tokens."""
from _util import esc, section_open, section_close

MARGIN_X = 20
TOP = 50            # space for the actor labels at the top
ROW_H = 56         # vertical step per message
COL_MIN = 130      # min spacing between lifelines
COL_PAD = 28       # extra spacing added per actor-name length factor
ACT_W = 12         # activation-bar half width
BOTTOM = 30


def _col_width(actors):
    longest = max((len(str(a)) for a in actors), default=4)
    return max(COL_MIN, longest * 8 + COL_PAD)


def render(block: dict) -> str:
    actors = [str(a) for a in block["actors"]]
    messages = block["messages"]
    idx = {a: i for i, a in enumerate(actors)}

    col_w = _col_width(actors)
    n = len(actors)
    lane_x = {a: MARGIN_X + col_w // 2 + idx[a] * col_w for a in actors}
    vb_w = MARGIN_X * 2 + col_w * n
    life_bottom = TOP + ROW_H * (len(messages) + 1)
    vb_h = life_bottom + BOTTOM

    svg = [f'<svg class="swimlane" viewBox="0 0 {round(vb_w)} {round(vb_h)}" '
           'role="img" aria-label="sequence diagram">',
           '<defs><marker id="vz-sa" viewBox="0 0 10 10" refX="9" refY="5" '
           'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
           '<path d="M0 0 L10 5 L0 10 z"/></marker></defs>']

    # actor headers + lifelines
    for a in actors:
        x = lane_x[a]
        svg.append(f'<line class="lane" x1="{x}" y1="{TOP}" x2="{x}" '
                   f'y2="{round(life_bottom)}"/>')
        svg.append(f'<text class="actor" x="{x}" y="32">{esc(a)}</text>')

    # messages, one per time row
    for k, m in enumerate(messages):
        frm, to = str(m["from"]), str(m["to"])
        if frm not in lane_x or to not in lane_x:
            continue
        y = TOP + ROW_H * (k + 1)
        x1, x2 = lane_x[frm], lane_x[to]
        is_return = bool(m.get("return"))

        # activation bar on the receiver's lifeline — runs the full row step so
        # its bottom reaches the next message line instead of floating mid-gap
        svg.append(f'<rect class="active" x="{round(x2 - ACT_W/2)}" '
                   f'y="{round(y)}" width="{ACT_W}" height="{ROW_H}" rx="2"/>')

        cls = "msg--return" if is_return else "msg"
        # nudge the arrow endpoint to the near edge of the activation bar
        edge = ACT_W / 2 if x2 > x1 else -ACT_W / 2
        if x1 == x2:  # self-message: a small loop back to the same lifeline
            loop = col_w * 0.32
            d = (f'M{round(x1)} {round(y)} C {round(x1+loop)} {round(y)}, '
                 f'{round(x1+loop)} {round(y+ROW_H*0.4)}, '
                 f'{round(x1+ACT_W/2)} {round(y+ROW_H*0.4)}')
            svg.append(f'<path class="{cls}" d="{d}" marker-end="url(#vz-sa)"/>')
            ly = y - 6
            lx = x1 + loop / 2
        else:
            x2e = x2 - edge
            svg.append(f'<line class="{cls}" x1="{round(x1)}" y1="{round(y)}" '
                       f'x2="{round(x2e)}" y2="{round(y)}" marker-end="url(#vz-sa)"/>')
            ly = y - 8
            lx = (x1 + x2) / 2

        if m.get("label"):
            svg.append(f'<text class="mlabel" x="{round(lx)}" y="{round(ly)}">'
                       f'{esc(m["label"])}</text>')

    svg.append('</svg>')
    return (section_open(block, wrap="wide")
            + "".join(svg)
            + section_close())
