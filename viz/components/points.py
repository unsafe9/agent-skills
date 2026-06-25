"""points — scannable list of claims, each with an optional supporting detail."""
from _util import esc, section_open, section_close
from _md import inline


def render(block: dict) -> str:
    parts = []
    if block.get("heading"):
        parts.append(f'<h2>{esc(block["heading"])}</h2>')
    items = []
    for item in block["items"]:
        li = f'<span class="pt-text">{inline(item["text"])}</span>'
        if item.get("detail"):
            li += f'<small>{inline(item["detail"])}</small>'
        items.append(f"<li>{li}</li>")
    parts.append('<ul class="points">' + "".join(items) + "</ul>")
    return (section_open(block, wrap="wrap")
            + "".join(parts)
            + section_close())
