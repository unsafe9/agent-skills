"""prose — a reading passage with optional heading and rich markdown body."""
from _util import esc, section_open, section_close
from _md import rich


def render(block: dict) -> str:
    parts = []
    if block.get("heading"):
        parts.append(f'<h2>{esc(block["heading"])}</h2>')
    parts.append(f'<div class="prose-block">{rich(block["body"])}</div>')
    return (section_open(block, wrap="prose")
            + "".join(parts)
            + section_close())
