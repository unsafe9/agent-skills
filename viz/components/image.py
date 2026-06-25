"""image — embed a LOCAL image file as a base64 data URI (fully offline).

render(block) receives an already-validated block dict and returns ONE complete
<section>…</section>. The heavy lifting — read the file, guess the mime type,
base64-encode, and apply aspect-ratio-respecting sizing — lives in
_util.embed_image; this renderer only frames the <img> in a <figure> with an
optional caption. A missing src degrades (inside embed_image) to a labeled
placeholder rather than breaking the build."""
from _util import esc, section_open, section_close, embed_image


def render(block: dict) -> str:
    img = embed_image(block["src"],
                      width=block.get("width"),
                      height=block.get("height"),
                      alt=block.get("alt", ""))
    caption = block.get("caption")
    cap = f"<figcaption>{esc(caption)}</figcaption>" if caption else ""
    return (section_open(block, cls="viz-image")
            + f'<figure class="vi-figure">{img}{cap}</figure>'
            + section_close())
