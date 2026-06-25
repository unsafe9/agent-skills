"""Inline and rich markdown helpers for prose-family components.

Only prose/callout/points/steps use these — other components use plain esc().
Leading underscore keeps build.py from treating this as a component."""
import re
from _util import esc as _esc


_SAFE_URL = re.compile(r'^(https?://|mailto:|/|\.\.?/)')


def _escape_raw(s: str) -> str:
    """HTML-escape without the token markup pass, used internally."""
    from html import escape
    return escape(str(s), quote=True)


def inline(s: str) -> str:
    """Render inline markdown to HTML fragments.

    Handles **bold**, *italic*, `code`, [text](url).
    Escapes everything else so user text can never inject markup.
    Link URLs are allow-listed to http/https/mailto/relative; javascript: is silently dropped.
    """
    # Work on escaped text so we don't double-escape, but we need to apply
    # patterns before escaping raw text. Strategy: tokenize the raw string into
    # safe (markup) and unsafe (literal) segments.
    out = []
    pos = 0
    s = str(s)
    # Combined pattern: links first (greedy), then bold, italic, code
    pattern = re.compile(
        r'\[([^\[\]]*)\]\(((?:[^()]|\([^()]*\))*)\)'  # [text](url) — url may hold one level of (parens)
        r'|\*\*(.+?)\*\*'                              # **bold** (may wrap inner emphasis)
        r'|\*([^*]+)\*'                                # *italic*
        r'|`([^`]+)`'                                  # `code`
    )
    for m in pattern.finditer(s):
        # literal text before this match
        out.append(_escape_raw(s[pos:m.start()]))
        if m.group(1) is not None:
            # link: [text](url)
            text = _escape_raw(m.group(1))
            url = m.group(2).strip()
            if _SAFE_URL.match(url):
                out.append(f'<a href="{_escape_raw(url)}">{text}</a>')
            else:
                # unsafe scheme — render as plain text
                out.append(text)
        elif m.group(3) is not None:
            # recurse so inner *italic* / `code` inside **bold** still render
            out.append(f'<strong>{inline(m.group(3))}</strong>')
        elif m.group(4) is not None:
            out.append(f'<em>{_escape_raw(m.group(4))}</em>')
        elif m.group(5) is not None:
            out.append(f'<code>{_escape_raw(m.group(5))}</code>')
        pos = m.end()
    out.append(_escape_raw(s[pos:]))
    return "".join(out)


def rich(s: str) -> str:
    """Multi-line markdown to HTML.

    Splits on blank lines into paragraphs. Consecutive `- ` lines become <ul><li>.
    Applies inline() within each element.
    """
    s = str(s)
    # Normalise line endings
    lines = s.replace("\r\n", "\n").replace("\r", "\n").splitlines()

    # Group lines into paragraph-blocks separated by blank lines
    groups: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if line.strip() == "":
            if current:
                groups.append(current)
                current = []
        else:
            current.append(line)
    if current:
        groups.append(current)

    parts = []
    for group in groups:
        # Within a group, split into consecutive runs of bullet vs. prose lines
        # so that `- ` lines always render as <ul>, even when mixed with prose.
        runs: list[tuple[str, list[str]]] = []  # (kind, lines)
        for ln in group:
            kind = "bullet" if ln.startswith("- ") else "prose"
            if runs and runs[-1][0] == kind:
                runs[-1][1].append(ln)
            else:
                runs.append((kind, [ln]))
        for kind, lines in runs:
            if kind == "bullet":
                items = "".join(f"<li>{inline(ln[2:])}</li>" for ln in lines)
                parts.append(f"<ul>{items}</ul>")
            else:
                text = " ".join(lines)
                parts.append(f"<p>{inline(text)}</p>")

    return "".join(parts)
