"""callout — a boxed aside with tone (note/tip/warn/danger)."""
from _util import esc, section_open, section_close
from _md import rich


def render(block: dict) -> str:
    tone = block.get("tone", "note")
    parts = []
    if block.get("title"):
        parts.append(f'<strong class="callout-title">{esc(block["title"])}</strong>')
    parts.append(f'<div class="callout-body">{rich(block["body"])}</div>')
    inner = "".join(parts)
    return (section_open(block, wrap="prose")
            + f'<div class="callout callout--{esc(tone)}">{inner}</div>'
            + section_close())
