"""bookmark — a link-preview card rendered purely from supplied fields.

Does NOT fetch anything. Domain fallbacks for title/site are derived from the
url at render time. Thumbnail and favicon are embedded as data URIs via
embed_image(); a missing favicon renders as a domain-letter monogram instead."""
from urllib.parse import urlparse
from _util import esc, section_open, section_close, embed_image


def _domain(url: str) -> str:
    """Strip scheme and path from url, return bare hostname (e.g. 'go.dev')."""
    try:
        host = urlparse(url).hostname or ""
        # drop leading www.
        return host[4:] if host.startswith("www.") else host
    except Exception:
        return url


def render(block: dict) -> str:
    url = block["url"]
    domain = _domain(url)

    title = block.get("title") or domain
    desc = block.get("desc", "")
    site = block.get("site") or domain
    thumb_path = block.get("thumb")
    favicon_path = block.get("favicon")

    # ── thumbnail (image-on-top layout when present) ──────────────────────
    if thumb_path:
        thumb_html = embed_image(thumb_path, alt=title, cls="bm-thumb")
    else:
        thumb_html = ""

    # ── site icon: embedded favicon or monogram ───────────────────────────
    if favicon_path:
        icon_html = embed_image(favicon_path, width=18, height=18,
                                alt=site, cls="bm-favicon")
    else:
        monogram = esc(domain[:1].upper() if domain else "?")
        icon_html = f'<span class="bm-monogram" aria-hidden="true">{monogram}</span>'

    # ── description (optional) ────────────────────────────────────────────
    desc_html = f'<p class="bm-desc">{esc(desc)}</p>' if desc else ""

    inner = (
        thumb_html
        + '<div class="bm-body">'
        +   f'<p class="bm-title">{esc(title)}</p>'
        +   desc_html
        +   '<div class="bm-site">'
        +     icon_html
        +     f'<span class="bm-site-name">{esc(site)}</span>'
        +   '</div>'
        + '</div>'
    )

    return (
        section_open(block, cls="", wrap="wrap")
        + f'<a class="bookmark" href="{esc(url)}" rel="noopener noreferrer" target="_blank">'
        + inner
        + '</a>'
        + section_close()
    )
