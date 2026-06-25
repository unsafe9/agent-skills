"""decision — interactive options that assemble into a copy-paste next-step prompt.

render(block) receives a block dict already validated against schema.yaml.
Returns ONE complete <section>…</section>. Escape every piece of user text.

composer.js queries:
  .decision                  — wraps each decision group
  .option[data-frag]         — clickable choice; .pick marks the recommended lean
  .option.sel                — set on the currently selected option (js toggles this)
  .ask-input[data-frag]      — optional free-text textarea (frag contains {v})
The #composer / #prompt-preview / #copy-btn are appended by build.py assemble(),
not by this renderer."""
from _util import esc, section_open, section_close


def render(block: dict) -> str:
    parts = []

    question = block.get("question", "")
    if question:
        parts.append(f'<h2>{esc(question)}</h2>')

    opts = []
    for opt in block.get("options", []):
        pick_cls = " pick" if opt.get("pick") else ""
        frag = esc(opt.get("frag", ""))
        inner = [f'<b>{esc(opt["label"])}</b>']
        if opt.get("detail"):
            inner.append(f'<p>{esc(opt["detail"])}</p>')
        opts.append(
            f'<button class="option{pick_cls}" data-frag="{frag}">'
            + "".join(inner)
            + "</button>"
        )
    parts.append('<div class="options">' + "".join(opts) + "</div>")

    ft = block.get("freetext")
    if ft:
        key = esc(block.get("key", ""))
        frag_attr = f'{esc(ft)}: {{v}}'
        parts.append(
            '<div class="freeinput">'
            + f'<label>{esc(ft)}</label>'
            + f'<textarea class="ask-input" data-frag="{frag_attr}"></textarea>'
            + "</div>"
        )

    return (
        section_open(block)
        + '<div class="decision">'
        + "".join(parts)
        + "</div>"
        + section_close()
    )
