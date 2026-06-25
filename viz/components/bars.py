"""bars — CSS bar chart, horizontal (default) or vertical.

render(block) receives an already-validated block dict. Returns ONE complete
<section>…</section>. Horizontal bars: label + track + value. Vertical bars:
lifted from present scroll shell .bars/.bar layout. Width/height is set via
CSS custom property --v (0..1 fraction of max)."""
from _util import esc, section_open, section_close

TONES = {"good", "bad", "accent"}


def render(block: dict) -> str:
    items = block["items"]
    direction = block.get("dir", "h")
    explicit_max = block.get("max")

    values = [item["value"] for item in items]
    try:
        numeric = [float(v) for v in values]
    except (TypeError, ValueError):
        numeric = list(range(len(values)))
    raw_max = max(numeric) if numeric else 1
    axis_max = float(explicit_max) if explicit_max is not None else raw_max
    if axis_max == 0:
        axis_max = 1

    heading = block.get("heading")
    head = f"<h2>{esc(heading)}</h2>" if heading else ""

    if direction == "v":
        # vertical bars — lifted from present scroll shell
        bar_els = []
        for item, num in zip(items, numeric):
            tone = item.get("tone")
            frac = max(0.0, num / axis_max)
            style = f"style=\"--v:{frac:.4f}\""
            cls = f" {tone}" if tone in TONES else ""
            bar_els.append(
                f'<div class="bar{cls}">'
                f'<i {style}></i>'
                f'<b>{esc(item["value"])}</b>'
                f'<span>{esc(item["label"])}</span>'
                f'</div>'
            )
        return (section_open(block, wrap="wide")
                + head
                + '<div class="bars bars-v">' + "".join(bar_els) + "</div>"
                + section_close())
    else:
        # horizontal bars — label + track + value pill
        bar_els = []
        for item, num in zip(items, numeric):
            tone = item.get("tone")
            frac = max(0.0, num / axis_max)
            style = f"style=\"--v:{frac:.4f}\""
            cls = f" {tone}" if tone in TONES else ""
            bar_els.append(
                f'<div class="hbar{cls}">'
                f'<span class="hbar-label">{esc(item["label"])}</span>'
                f'<div class="hbar-track"><div class="hbar-fill" {style}></div></div>'
                f'<span class="hbar-val">{esc(item["value"])}</span>'
                f'</div>'
            )
        return (section_open(block)
                + head
                + '<div class="hbars">' + "".join(bar_els) + "</div>"
                + section_close())
