"""badges — a row of small labeled status pills.

render(block) receives an already-validated block dict. Returns ONE complete
<section>…</section>. Each badge has required text and optional tone."""
from _util import esc, section_open, section_close

TONES = {"good", "warn", "bad", "accent", "muted"}


def render(block: dict) -> str:
    heading = block.get("heading")
    head = f"<h2>{esc(heading)}</h2>" if heading else ""

    pills = []
    for item in block["items"]:
        tone = item.get("tone")
        cls = f"badge {tone}" if tone in TONES else "badge"
        pills.append(f'<span class="{cls}">{esc(item["text"])}</span>')

    return (section_open(block)
            + head
            + '<div class="badges">' + "".join(pills) + "</div>"
            + section_close())
