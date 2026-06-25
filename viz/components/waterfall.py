"""waterfall — additive breakdown: how a total decomposes into stacked parts.

render(block) receives an already-validated block dict. Returns ONE complete
<section>…</section>. A stacked bar lays every part end-to-end so the parts
visibly sum to the whole; per-part rows give label, value (+unit) and % of total;
a final Total bar shows the full sum."""
from _util import esc, section_open, section_close

TONES = {"good", "bad", "accent"}


def _fmt(num: float) -> str:
    """Drop a trailing .0 so whole numbers read clean; keep real fractions."""
    return str(int(num)) if num == int(num) else f"{num:g}"


def render(block: dict) -> str:
    items = block["items"]
    unit = block.get("unit", "")
    total_label = block.get("total_label", "Total")
    suffix = f" {esc(unit)}" if unit else ""

    nums = []
    for item in items:
        try:
            nums.append(float(item["value"]))
        except (TypeError, ValueError):
            nums.append(0.0)
    total = sum(nums)
    denom = total if total else 1.0

    # stacked bar — segments laid end-to-end, each sized by its share of the total
    segs = []
    for item, num in zip(items, nums):
        tone = item.get("tone")
        cls = f"wf-seg {tone}" if tone in TONES else "wf-seg"
        frac = max(0.0, num / denom)
        title = esc(f'{item["label"]}: {_fmt(num)}{unit}'.strip())
        segs.append(
            f'<span class="{cls}" style="--w:{frac:.4f}" title="{title}"></span>'
        )
    stacked = f'<div class="wf-stack">{"".join(segs)}</div>'

    # per-part rows — label · value(+unit) · % of total
    rows = []
    for item, num in zip(items, nums):
        tone = item.get("tone")
        chip = f"wf-chip {tone}" if tone in TONES else "wf-chip"
        pct = 100.0 * num / denom
        rows.append(
            f'<div class="wf-row">'
            f'<span class="{chip}"></span>'
            f'<span class="wf-label">{esc(item["label"])}</span>'
            f'<span class="wf-val">{esc(_fmt(num))}{suffix}</span>'
            f'<span class="wf-pct">{pct:.0f}%</span>'
            f'</div>'
        )

    # final cumulative total
    total_row = (
        f'<div class="wf-row wf-total">'
        f'<span class="wf-label">{esc(total_label)}</span>'
        f'<span class="wf-val">{esc(_fmt(total))}{suffix}</span>'
        f'<span class="wf-pct">100%</span>'
        f'</div>'
    )

    return (section_open(block, cls="waterfall")
            + stacked
            + '<div class="wf-rows">' + "".join(rows) + total_row + "</div>"
            + section_close())
