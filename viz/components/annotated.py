"""annotated — source shown verbatim with per-line notes, an inline code review.

Each line is a grid row: monospace code cell on the left, markdown-inline note
cell on the right (wide). `mark` (add/del/warn/focus) tints the whole row from
skin tokens. Code whitespace/indentation is preserved via esc() + white-space:pre."""
from _util import esc, section_open, section_close
from _md import inline


_MARKS = {"add", "del", "warn", "focus"}


def render(block: dict) -> str:
    lang = block.get("lang", "")
    filename = block.get("filename", "")
    lines = block.get("lines") or []

    header = ""
    if filename or lang:
        parts = []
        if filename:
            parts.append(f'<span class="code-filename">{esc(filename)}</span>')
        if lang:
            parts.append(f'<span class="code-lang">{esc(lang)}</span>')
        header = '<div class="anno-header">' + "".join(parts) + "</div>"

    rows = []
    for item in lines:
        code = str(item.get("code", ""))
        note = item.get("note")
        mark = item.get("mark")

        row_cls = "anno-row"
        if mark in _MARKS:
            row_cls += f" anno-{mark}"

        # empty code line still needs a visible cell height
        code_html = esc(code) if code != "" else ""
        code_cell = f'<div class="anno-code">{code_html}</div>'

        if note:
            note_cell = f'<div class="anno-note">{inline(note)}</div>'
        else:
            note_cell = '<div class="anno-note anno-note-empty"></div>'

        rows.append(f'<div class="{row_cls}">{code_cell}{note_cell}</div>')

    body = header + '<div class="anno-grid">' + "".join(rows) + "</div>"
    return section_open(block, cls="annotated", wrap="wide") + body + section_close()
