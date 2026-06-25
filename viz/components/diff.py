"""diff — unified diff rendered line-by-line: + added (--good), - removed (--bad),
@@ hunk headers (--accent), everything else context (--muted). Content is
preserved verbatim; optional filename header.

`lineno` adds a two-column gutter (old | new). The numbers come from the `@@ -a +b @@`
hunk headers when present, so the gutter shows the real file line numbers; a patch
with no real hunk header just counts from 1."""
import re
from _util import esc, section_open, section_close

# real unified-diff hunk header: @@ -oldStart[,n] +newStart[,n] @@
_HUNK = re.compile(r'^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@')


def render(block: dict) -> str:
    filename = block.get("filename", "")
    lineno = bool(block.get("lineno"))
    patch = str(block.get("patch", ""))

    header = ""
    if filename:
        header = f'<div class="diff-header">{esc(filename)}</div>'

    lines = patch.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]

    old_no = new_no = 1
    max_no = 1
    rows = []
    for line in lines:
        if line.startswith("@@"):
            cls, ocol, ncol = "diff-hunk", "", ""
            hm = _HUNK.match(line)
            if hm:
                old_no, new_no = int(hm.group(1)), int(hm.group(2))
        elif line.startswith("+"):
            cls, ocol, ncol = "diff-add", "", str(new_no)
            new_no += 1
        elif line.startswith("-"):
            cls, ocol, ncol = "diff-del", str(old_no), ""
            old_no += 1
        else:
            cls, ocol, ncol = "diff-ctx", str(old_no), str(new_no)
            old_no += 1
            new_no += 1
        max_no = max(max_no, old_no, new_no)
        gutter = (f'<span class="ln">{ocol}</span><span class="ln">{ncol}</span>'
                  if lineno else "")
        rows.append(f'<span class="cl {cls}">{gutter}'
                    f'<span class="lc">{esc(line)}</span></span>')

    gw = len(str(max_no))
    pre = f'<pre class="lined" style="--gw:{gw}ch">' if lineno else "<pre>"
    body = header + pre + "<code>" + "".join(rows) + "</code></pre>"
    return section_open(block, wrap="prose") + body + section_close()
