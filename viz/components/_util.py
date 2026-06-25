"""Shared helpers for component renderers. Not a component (leading underscore →
build.py skips it during discovery)."""
import base64
import importlib.util
import mimetypes
from html import escape as _escape
from pathlib import Path


def esc(value) -> str:
    """HTML-escape any user-supplied scalar (quotes included) for safe markup."""
    return _escape(str(value), quote=True)


def section_open(block: dict, *, cls: str = "", wrap: str = "wrap") -> str:
    """Open a block's <section>, wiring the optional nav-dot label.

    `cls` is extra section classes (e.g. 'hero', 'band'); `wrap` is the width
    container the content sits in ('wrap' | 'prose' | 'wide'). Returns the opening
    `<section ...><div class="<wrap> reveal">` — close with `section_close()`.
    """
    attrs = []
    classes = " ".join(c for c in cls.split() if c)
    if classes:
        attrs.append(f'class="{classes}"')
    nav = block.get("nav")
    if nav:
        attrs.append(f'data-nav="{esc(nav)}"')
    head = "<section" + ("" if not attrs else " " + " ".join(attrs)) + ">"
    return f'{head}<div class="{wrap} reveal">'


def section_close() -> str:
    return "</div></section>"


_CHILD_RENDERERS = {}


def render_block(block: dict) -> str:
    """Render a nested child block to its <section>, for container blocks like
    `group`. Mirrors build.py's load_renderer dispatch; cached per type. The child
    is already validated (build.py recurses into nested `kind: blocks` fields)."""
    t = block["type"]
    fn = _CHILD_RENDERERS.get(t)
    if fn is None:
        path = Path(__file__).resolve().parent / f"{t}.py"
        spec = importlib.util.spec_from_file_location(f"viz_child_{t}", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        fn = mod.render
        _CHILD_RENDERERS[t] = fn
    return fn(block)


_IMG_MIME = {".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg",
             ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp",
             ".avif": "image/avif", ".bmp": "image/bmp", ".ico": "image/x-icon"}


def _css_len(v) -> str:
    """A bare number means px; anything else (e.g. '60%', '4rem') passes through."""
    s = str(v).strip()
    return f"{s}px" if s.isdigit() else s


def _dimension_style(width, height) -> str:
    """Size policy: respect the source aspect ratio unless BOTH dims are pinned.
    width-only -> height auto; height-only -> width auto; neither -> natural size
    capped to the column."""
    if width and height:
        return f"width:{_css_len(width)};height:{_css_len(height)}"
    if width:
        return f"width:{_css_len(width)};height:auto;max-width:100%"
    if height:
        return f"height:{_css_len(height)};width:auto"
    return "max-width:100%;height:auto"


def embed_image(src, *, width=None, height=None, alt="", cls="") -> str:
    """Read a LOCAL image file and return an <img> with its bytes inlined as a
    base64 data URI, keeping the page a single offline file (the build's offline
    guard allows data: URIs but blocks remote src). A missing file degrades to a
    labeled placeholder instead of breaking the build, so one bad path never
    fails the whole page."""
    p = Path(str(src)).expanduser()
    if not p.is_file():
        return f'<div class="img-missing">Image missing: {esc(src)}</div>'
    mime = mimetypes.guess_type(p.name)[0] or _IMG_MIME.get(p.suffix.lower(), "image/png")
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    class_attr = f' class="{esc(cls)}"' if cls else ""
    return (f'<img{class_attr} src="data:{mime};base64,{b64}" alt="{esc(alt)}"'
            f' style="{_dimension_style(width, height)}">')
