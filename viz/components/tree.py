"""tree — file/dir or any hierarchy with CSS connector lines.

render(block) receives an already-validated block dict. Returns ONE complete
<section>…</section>. Nodes nest to any depth; validator only checks root is
a map, so we recurse ourselves. Add/mod/del badges are rendered inline."""
from _util import esc, section_open, section_close

BADGE_CLS = {"add": "b-add", "mod": "b-mod", "del": "b-del"}
KIND_CLS = {"dir": "t-dir", "file": "t-file"}


def _node(node: dict) -> str:
    label = node.get("label", "")
    kind = node.get("kind", "file")
    badge = node.get("badge")
    children = node.get("children", [])

    kind_cls = KIND_CLS.get(kind, "t-file")
    label_html = f'<span class="{kind_cls}">{esc(label)}</span>'
    if badge and badge in BADGE_CLS:
        label_html += f' <span class="t-badge {BADGE_CLS[badge]}">{esc(badge)}</span>'

    inner = label_html
    if children:
        lis = "".join(f"<li>{_node(c)}</li>" for c in children)
        inner += f"<ul>{lis}</ul>"
    return inner


def render(block: dict) -> str:
    heading = block.get("heading")
    head = f"<h2>{esc(heading)}</h2>" if heading else ""

    root = block["root"]
    tree_html = f'<ul class="tree"><li>{_node(root)}</li></ul>'

    return (section_open(block)
            + head
            + tree_html
            + section_close())
