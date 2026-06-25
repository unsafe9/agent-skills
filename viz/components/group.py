"""group — a titled cluster that wraps related child blocks under one heading and
ONE shared section padding, optionally in two columns. Children render through the
normal per-type dispatch (render_block); this renderer neutralises their individual
section chrome via group.css so the cluster reads as a single organised unit instead
of N full-screen islands. Two-column groups break out to the wide `full` container
and collapse to one column on narrow screens.

tone:accent paints the cluster as a subtly accent-tinted full-bleed band for
emphasis — a token mix that stays readable on every skin."""
from _util import esc, section_open, section_close, render_block


def render(block: dict) -> str:
    try:
        columns = int(block.get("columns", 1) or 1)
    except (TypeError, ValueError):
        columns = 1
    tone = block.get("tone")
    heading = block.get("heading")

    cls = "group"
    if tone == "accent":
        cls += " group--accent"
    if columns == 2:
        cls += " group--cols2"
    wrap = "wide" if columns == 2 else "wrap"

    head = f"<h2>{esc(heading)}</h2>" if heading else ""
    children = "".join(render_block(c) for c in block.get("blocks", []))
    return (section_open(block, cls=cls, wrap=wrap)
            + head
            + f'<div class="group-grid">{children}</div>'
            + section_close())
