"""code — monospace code block with optional filename/lang header, lightweight
syntax highlighting, full-row line highlighting, and an optional line-number
gutter.

Highlighting is a small build-time tokenizer (comments, strings, numbers, and a
per-language keyword set) emitting .cmt/.str/.num/.key spans — not a real parser,
but enough to read offline with no JS. `highlight` tints whole rows. `lineno` (or
giving `start`) turns on a gutter numbered from `start` (default 1) so a block can
show the real file line numbers it was lifted from."""
import re
from _util import esc, section_open, section_close

# per-language keyword sets; an unknown/absent lang falls back to the union so a
# bare snippet still gets sensible coloring.
_KEYWORDS = {
    "python": "def class return if elif else for while import from as with try except "
              "finally raise yield lambda pass break continue in is not and or None True "
              "False global nonlocal assert del async await match case",
    "javascript": "function return if else for while do const let var class extends super new "
                  "this import export default async await try catch finally throw typeof "
                  "instanceof switch case break continue null undefined true false of in static "
                  "get set",
    "typescript": "function return if else for while const let var class extends implements "
                  "interface type enum new this import export default async await try catch "
                  "finally throw switch case break continue null undefined true false of in "
                  "public private protected readonly as keyof typeof namespace declare",
    "go": "func return if else for range var const type struct interface map chan go defer "
          "package import switch case default break continue fallthrough select nil true false goto",
    "rust": "fn let mut return if else for while loop match struct enum impl trait pub use mod "
            "const static ref move async await where as dyn self Self crate super true false "
            "Some None Ok Err unsafe",
    "java": "public private protected class interface enum extends implements return if else for "
            "while do switch case break continue new this super import package static final void "
            "int long double float boolean char try catch finally throw throws null true false abstract",
    "c": "int long short char void float double struct union enum return if else for while do "
         "switch case break continue static const unsigned signed sizeof typedef extern goto NULL "
         "true false",
    "sql": "select from where group by order having join left right inner outer on as insert into "
           "values update set delete create table drop alter index and or not null distinct limit",
    "bash": "if then else elif fi for in do done while case esac function return local export echo "
            "exit set source",
}
_ALIAS = {"py": "python", "js": "javascript", "jsx": "javascript", "ts": "typescript",
          "tsx": "typescript", "golang": "go", "rs": "rust", "sh": "bash", "shell": "bash",
          "zsh": "bash", "c++": "c", "cpp": "c", "h": "c"}
_DEFAULT_KW = set(" ".join(_KEYWORDS.values()).split())

# one pass: comment | string | number | identifier. Strings/comments are matched
# whole so a `#` or `//` inside a literal never starts a false comment.
_TOKEN = re.compile(
    r'(?P<cmt>#.*|//.*|/\*.*?\*/)'
    r'|(?P<str>"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'|`(?:\\.|[^`\\])*`)'
    r'|(?P<num>\b\d[\d_]*\.?\d*(?:[eE][+-]?\d+)?\b)'
    r'|(?P<id>[A-Za-z_]\w*)'
)


def _keywords(lang: str) -> set:
    lang = _ALIAS.get(lang.lower(), lang.lower())
    kw = _KEYWORDS.get(lang)
    return set(kw.split()) if kw else _DEFAULT_KW


def _highlight(line: str, kws: set) -> str:
    """Tokenize one line into escaped HTML with .cmt/.str/.num/.key spans. Every
    slice is escaped individually, so markup never leaks from the source."""
    out, pos = [], 0
    for m in _TOKEN.finditer(line):
        if m.start() > pos:
            out.append(esc(line[pos:m.start()]))
        kind, text = m.lastgroup, esc(m.group())
        if kind == "id":
            out.append(f'<span class="key">{text}</span>' if m.group() in kws else text)
        else:
            out.append(f'<span class="{kind}">{text}</span>')
        pos = m.end()
    if pos < len(line):
        out.append(esc(line[pos:]))
    return "".join(out)


def render(block: dict) -> str:
    lang = block.get("lang", "")
    filename = block.get("filename", "")
    highlight = set(block.get("highlight") or [])
    start = block.get("start")
    lineno = bool(block.get("lineno")) or start is not None
    start = int(start) if start is not None else 1
    source = str(block.get("code", ""))
    kws = _keywords(lang)

    header = ""
    if filename or lang:
        parts = []
        if filename:
            parts.append(f'<span class="code-filename">{esc(filename)}</span>')
        if lang:
            parts.append(f'<span class="code-lang">{esc(lang)}</span>')
        header = '<div class="code-header">' + "".join(parts) + "</div>"

    lines = source.split("\n")
    # strip a single trailing empty line that YAML block scalars add
    if lines and lines[-1] == "":
        lines = lines[:-1]

    rows = []
    for idx, line in enumerate(lines):
        cls = "cl hl" if (idx + 1) in highlight else "cl"
        gutter = f'<span class="ln">{start + idx}</span>' if lineno else ""
        rows.append(f'<span class="{cls}">{gutter}'
                    f'<span class="lc">{_highlight(line, kws)}</span></span>')

    gw = len(str(start + max(len(lines) - 1, 0)))
    pre = f'<pre class="lined" style="--gw:{gw}ch">' if lineno else "<pre>"
    body = header + pre + "<code>" + "".join(rows) + "</code></pre>"
    return section_open(block, wrap="prose") + body + section_close()
