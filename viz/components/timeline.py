"""timeline — vertical sequence of events down a rail.

Each event has: when (required), title (required), body (optional detail),
tone (good/warn/bad/accent — colors the dot)."""
from _util import esc, section_open, section_close

TONES = {"good", "bad", "warn", "accent"}


def render(block: dict) -> str:
    heading = block.get("heading", "")
    events = block.get("events", [])

    parts = []
    if heading:
        parts.append(f"<h2>{esc(heading)}</h2>")

    items = []
    for ev in events:
        tone = ev.get("tone")
        dot_cls = f"tl-dot {tone}" if tone in TONES else "tl-dot"
        inner = [
            f'<div class="{dot_cls}"></div>',
            f'<div class="tl-when">{esc(ev["when"])}</div>',
            f'<div class="tl-title">{esc(ev["title"])}</div>',
        ]
        if ev.get("body"):
            inner.append(f'<div class="tl-body">{esc(ev["body"])}</div>')
        items.append('<div class="tl-event">' + "".join(inner) + "</div>")

    parts.append('<div class="tl-rail">' + "".join(items) + "</div>")
    return section_open(block) + "".join(parts) + section_close()
