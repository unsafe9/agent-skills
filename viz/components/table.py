"""table — comparison table with optional per-cell tinting.

render(block) receives an already-validated block dict. Returns ONE complete
<section>…</section>. Each row cell is either a plain string or a map
{v: text, tone: good|bad|warn}. Use wrap="wide" for 4+ columns."""
from _util import esc, section_open, section_close

TONES = {"good", "bad", "warn"}


def _cell(cell) -> str:
    if isinstance(cell, dict):
        tone = cell.get("tone")
        cls = f' class="{tone}"' if tone in TONES else ""
        return f"<td{cls}>{esc(cell.get('v', ''))}</td>"
    return f"<td>{esc(cell)}</td>"


def render(block: dict) -> str:
    columns = block["columns"]
    rows = block["rows"]
    wrap = "wide" if len(columns) >= 4 else "wrap"

    heading = block.get("heading")
    head = f"<h2>{esc(heading)}</h2>" if heading else ""

    ths = "".join(f"<th>{esc(c)}</th>" for c in columns)
    thead = f"<thead><tr>{ths}</tr></thead>"

    trows = []
    for row in rows:
        cells = "".join(_cell(c) for c in row)
        trows.append(f"<tr>{cells}</tr>")
    tbody = "<tbody>" + "".join(trows) + "</tbody>"

    return (section_open(block, wrap=wrap)
            + head
            + '<div class="table-scroll">'
            + f"<table>{thead}{tbody}</table>"
            + "</div>"
            + section_close())
