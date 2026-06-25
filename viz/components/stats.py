"""stats — big-number callouts. Reference component; copy this as the template.

render(block) receives a block dict the engine has ALREADY validated against
schema.yaml, so trust the shape: required fields are present, enums are legal.
Return ONE complete <section>…</section> string. Escape every piece of user text
with esc() so data can never break the markup."""
from _util import esc, section_open, section_close

TONES = {"good", "bad", "accent"}


def render(block: dict) -> str:
    cards = []
    for item in block["items"]:
        tone = item.get("tone")
        n_cls = f"n {tone}" if tone in TONES else "n"
        parts = [f'<div class="{n_cls}">{esc(item["n"])}</div>',
                 f'<div class="l">{esc(item["l"])}</div>']
        if item.get("delta"):
            parts.append(f'<div class="delta">{esc(item["delta"])}</div>')
        cards.append('<div class="stat">' + "".join(parts) + "</div>")
    return (section_open(block)
            + '<div class="stats">' + "".join(cards) + "</div>"
            + section_close())
