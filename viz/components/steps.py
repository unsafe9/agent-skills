"""steps — ordered procedure with numbered steps, each a title plus optional detail."""
from _util import esc, section_open, section_close
from _md import rich


def render(block: dict) -> str:
    parts = []
    if block.get("heading"):
        parts.append(f'<h2>{esc(block["heading"])}</h2>')
    items = []
    for item in block["items"]:
        inner = f'<span class="step-title">{esc(item["title"])}</span>'
        if item.get("body"):
            inner += f'<div class="step-body">{rich(item["body"])}</div>'
        items.append(f"<li>{inner}</li>")
    parts.append('<ol class="steps">' + "".join(items) + "</ol>")
    return (section_open(block, wrap="wrap")
            + "".join(parts)
            + section_close())
