"""cards — peer items in a responsive grid (4 items balance to 2×2).

render(block) receives an already-validated block dict. Returns ONE complete
<section>…</section>. Each card has a required title, optional body, badge,
and bullets list."""
from _util import esc, section_open, section_close


def render(block: dict) -> str:
    heading = block.get("heading")
    head = f"<h2>{esc(heading)}</h2>" if heading else ""

    card_els = []
    for item in block["items"]:
        parts = []
        if item.get("badge"):
            parts.append(f'<span class="badge-tag">{esc(item["badge"])}</span>')
        parts.append(f'<h3>{esc(item["title"])}</h3>')
        if item.get("body"):
            parts.append(f"<p>{esc(item['body'])}</p>")
        bullets = item.get("bullets")
        if bullets:
            lis = "".join(f"<li>{esc(b)}</li>" for b in bullets)
            parts.append(f"<ul>{lis}</ul>")
        card_els.append('<div class="card">' + "".join(parts) + "</div>")

    return (section_open(block)
            + head
            + '<div class="cards">' + "".join(card_els) + "</div>"
            + section_close())
