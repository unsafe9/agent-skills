#!/usr/bin/env python3
"""Assemble + verify a single self-contained offline present page from parts.

At authoring time the model outputs ONLY a body fragment + a skin pick. This
script mechanically assembles the shell + base.css + skin + engine + body into
one offline HTML file. The CSS scaffold, JS engine, and page chrome never enter
model output — that is the token/latency lever.

Cascade is base -> skin -> space (spacing scale) -> module-structural -> shell-structural:
  <head> emits <style>{{CSS}}</style> (= base.css, skins/<name>.css, space.css, then
  each allowlisted module's contract/<mod>.css) ABOVE the shell's literal structural
  <style>. So the skin :root overrides base tokens; space.css then sets the shared
  gap/pad ladder (--gap*/--pad/--rhythm); module + shell structural sizing win over
  the skin and are immune to reskinning (a shell may rescale the ladder for itself).

Usage:
  build.py --style {scroll|slides|dashboard|cheatsheet|compare|diagram} --body frag.html [--skin warm-paper] [--seed 7] [--out path]
  build.py --check --style scroll --body frag.html   # body-lint + base-coverage
  build.py --lint-skins                              # contrast + structural audit

Extending:
  Add a STYLE: drop shells/<name>/shell.html (+ engine.js if interactive), add
  <name> to the --style choices below, write shells/<name>/modules listing its
  contract/ modules, and document its vocabulary rows in those module files. A
  module may also ship contract/<mod>.css for shared primitive sizing, injected
  wherever it is allowlisted. Add a skin: drop a :root-tokens-only
  skins/<name>.css and run --lint-skins.
"""
import argparse
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Placeholder tokens that must appear EXACTLY ONCE in each shell.
PLACEHOLDERS = ("{{CSS}}", "{{JS}}", "{{BODY}}")

# Shell-chrome ids the engine/footer wire up — never authored as fragment
# vocabulary, so they are excluded from id-lint. (See parse_module's not-lint note.)
CHROME_IDS = {"progress", "bar", "counter", "modeBtn", "deck", "overview"}

# Each style declares which per-capability vocabulary modules (under contract/) it
# composes from, in its own shells/<style>/modules file — the single source of
# truth, read by style_modules() and by the authoring model. A style's lint
# allowlist is the UNION of just those modules, so e.g. a dashboard body using a
# compare-only `.radar` is rejected.

# WCAG 2.x AA threshold for normal-size text.
WCAG_AA_NORMAL = 4.5


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def pick_skin(seed):
    skins = sorted(p.stem for p in (ROOT / "skins").glob("*.css"))
    if not skins:
        sys.exit("error: no skins found in skins/")
    rng = random.Random(seed)
    return rng.choice(skins)


def substitute_once(html: str, token: str, value: str, shell_name: str) -> str:
    """Replace a placeholder, asserting it occurs EXACTLY once in the shell.

    Guards the Step-0 bug: a placeholder leaking into a comment (or missing
    entirely) would inject the payload twice / not at all. Fail loudly instead.
    """
    n = html.count(token)
    if n != 1:
        sys.exit(
            f"error: placeholder {token} occurs {n}x in {shell_name} "
            f"(expected exactly 1). Each placeholder must appear only in its "
            f"single real injection slot."
        )
    return html.replace(token, value)


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------

def assemble(style: str, body_text: str, skin: str) -> str:
    shell_path = ROOT / "shells" / style / "shell.html"
    engine_path = ROOT / "shells" / style / "engine.js"
    base_path = ROOT / "base.css"
    skin_path = ROOT / "skins" / f"{skin}.css"
    space_path = ROOT / "space.css"
    for p in (shell_path, base_path, skin_path, space_path):
        if not p.exists():
            sys.exit(f"error: missing required input: {p}")

    # Spacing scale: one shared elastic ladder of gap/padding tokens, injected after
    # the skin (so it is skin-immune) and before the modules/shell that read it, so
    # every gap/pad resolves to --gap*/--pad/--rhythm and a shell can rescale the whole
    # ladder for its context by redefining the tokens in its own :root.
    css = read(base_path).rstrip("\n") + "\n\n" + read(skin_path)
    css += "\n\n" + read(space_path)
    # Module-structural CSS: a vocabulary module may ship contract/<name>.css of
    # shared sizing for its primitives (e.g. figures sizes .tree/.layers/the SVGs).
    # Injected after the skin so structural sizing is skin-immune, and only for the
    # modules this style allowlists — so the same primitive is sized wherever it is
    # usable, with no per-shell duplication. The shell's own <style> still loads last
    # and may override for its context.
    for mod in style_modules(style):
        mod_css = ROOT / "contract" / f"{mod}.css"
        if mod_css.exists():
            css += "\n\n" + read(mod_css)
    # Static styles (dashboard, cheatsheet) carry no interactive engine: a missing
    # engine file means the {{JS}} slot is filled with the empty string. Interactive
    # styles share ONE composer block (shells/composer.js) assembled in after the
    # engine — not duplicated per engine, and a no-op on a page with no #composer.
    if engine_path.exists():
        composer_path = ROOT / "shells" / "composer.js"
        if not composer_path.exists():
            sys.exit(f"error: missing shared composer: {composer_path}")
        js = read(engine_path).rstrip("\n") + "\n\n" + read(composer_path)
    else:
        js = ""

    shell_label = f"{style}/shell.html"
    html = read(shell_path)
    html = substitute_once(html, "{{CSS}}", css, shell_label)
    html = substitute_once(html, "{{JS}}", js, shell_label)
    html = substitute_once(html, "{{BODY}}", body_text, shell_label)

    # ASSERT: assembly is complete and fully offline.
    if "{{" in html:
        leftover = html[html.index("{{"):html.index("{{") + 40]
        sys.exit(f"error: unsubstituted placeholder remains: {leftover!r}")
    for ref in ("http://", "https://", "<link", "url(http"):
        if ref in html:
            sys.exit(f"error: external resource reference found: {ref!r}")
    m = re.search(r'\bsrc\s*=\s*["\']([^"\']+)', html)
    if m and not m.group(1).startswith("data:"):
        sys.exit(f"error: external src= reference found: {m.group(1)!r}")
    return html


# ---------------------------------------------------------------------------
# Contract manifest parsing  (contract/<module>.md §1 parse contract)
# ---------------------------------------------------------------------------
#
# The vocabulary lives in nine per-capability module files under contract/
# (base, prose, figures, decide, slides, dashboard, cheatsheet, compare,
# canvas). Each file holds ONE GFM table in the shared format below; contract.md
# itself no longer carries the table. A style's allowlist is the UNION of the
# modules its shells/<style>/modules file names — see style_modules()/parse_modules().

MANIFEST_HEADER = "| token | styled in | when to use | DOM shape |"


def parse_module(name: str):
    """Parse contract/<name>.md's vocabulary table — one module's lint allowlist.

    Returns (classes, ids, styled_in) where:
      classes / ids   = allowlist sets (own-token rows + sub-element classes
                        harvested from every DOM-shape cell)
      styled_in       = {selector: set of 'base'/'scroll'/'slides'/…} for own-token
                        rows only (the base-coverage source of truth).

    Table format this depends on (keep each contract/<module>.md table in step):
      - The module's vocabulary is the single GFM pipe table whose header row is
        exactly MANIFEST_HEADER. Any title / description / composition-note prose
        ABOVE the table is ignored — we anchor on that header, then read every
        following `|`-delimited row until the first non-table line; the `|---|`
        separator row is skipped.
      - token (col 1): back-tick-wrapped, comma-separated selectors — each a
        literal `.class`, a literal `#id`, or a bare HTML element. We strip
        back-ticks, split on `,`, and record every `.`/`#` selector's remaining
        text as an allowed class/id token. Bare element selectors carry no token.
        Compound/descendant selectors are not used in col 1.
      - styled in (col 2): comma-separated source keywords — base, a shell (scroll
        / slides / dashboard / cheatsheet / compare / diagram), or a vocabulary
        module whose contract/<mod>.css sizes the primitive (e.g. figures) —
        possibly with a parenthetical selector qualifier; we extract just the
        keywords. It is the proof that no token is naked — base_coverage()
        re-verifies it against base.css, the shells, and the module CSS partials.
      - DOM shape (col 4): the literal markup the fragment emits; we harvest every
        `class="…"`/`id="…"` and back-ticked `.x`/`#x` from it, so sub-element
        classes documented inside a parent (e.g. `.col`, `.sc-fill`) join the
        allowlist without needing their own row.

    Not-lint targets handled outside this function (allowed though not own-token
    rows): shell-chrome ids the engine wires up (CHROME_IDS, excluded in
    lint_body) and any id named locally inside an <svg> (skipped via _svg_ranges)
    — e.g. a <marker id="ah"> referenced by marker-end="url(#ah)".
    """
    path = ROOT / "contract" / f"{name}.md"
    if not path.exists():
        sys.exit(f"error: missing contract module: {path}")
    text = read(path)
    lines = text.splitlines()
    try:
        start = next(i for i, ln in enumerate(lines) if ln.strip() == MANIFEST_HEADER)
    except StopIteration:
        sys.exit(f"error: manifest header not found in {path}: {MANIFEST_HEADER!r}")

    classes, ids = set(), set()
    styled_in = {}

    for ln in lines[start + 1:]:
        if not ln.lstrip().startswith("|"):
            break
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        token_cell, styled_cell = cells[0], cells[1]
        # skip the |---|---| separator row
        if set(token_cell.replace("-", "").replace(":", "")) == set():
            continue

        # column 2 may carry per-selector qualifiers, e.g.
        # "scroll (`.hero`), slides (`.title`)" or "base (`.col h3`), slides (`.cols`)".
        # The source keyword is one of base/scroll/slides/dashboard/cheatsheet
        # regardless of any parenthetical selector that qualifies WHICH selector
        # lives there.
        where = set(re.findall(r'\b(base|scroll|slides|dashboard|cheatsheet|compare|diagram)\b', styled_cell))

        # column 1 — back-ticked, comma-separated own-token selectors
        for sel in _split_ticked(token_cell):
            if sel.startswith("."):
                classes.add(sel[1:])
                styled_in.setdefault(sel, set()).update(where)
            elif sel.startswith("#"):
                ids.add(sel[1:])
                styled_in.setdefault(sel, set()).update(where)
            # bare element selectors carry no allowlist token

        # column 4 — harvest sub-element classes/ids from the DOM-shape cell
        shape_cell = cells[3]
        for cls in re.findall(r'class="([^"]+)"', shape_cell):
            classes.update(cls.split())
        for idv in re.findall(r'id="([^"]+)"', shape_cell):
            ids.add(idv)
        for sel in re.findall(r'`([.#][A-Za-z0-9_-]+)`', shape_cell):
            (classes if sel[0] == "." else ids).add(sel[1:])

    return classes, ids, styled_in


def parse_modules(names):
    """Union the (classes, ids, styled_in) of the named contract/ modules.

    The allowlist a --check run lints against = the union of just the modules the
    style declares (see style_modules), NOT every module. styled_in maps merge by
    union per selector so a selector documented in two modules keeps both sources.
    """
    classes, ids = set(), set()
    styled_in = {}
    for name in names:
        c, i, s = parse_module(name)
        classes |= c
        ids |= i
        for sel, where in s.items():
            styled_in.setdefault(sel, set()).update(where)
    return classes, ids, styled_in


def style_modules(style: str):
    """The vocabulary modules a style composes from — read from shells/<style>/modules.

    Single source of truth: build.py and the authoring model read the same file,
    which lists module names (whitespace-separated), e.g. `base prose figures decide`.
    """
    path = ROOT / "shells" / style / "modules"
    if not path.exists():
        sys.exit(f"error: missing module manifest: {path}")
    return read(path).split()


def _split_ticked(cell: str):
    """Strip back-ticks, split on commas, trim each selector."""
    out = []
    for chunk in cell.split(","):
        s = chunk.strip().strip("`").strip()
        if s:
            out.append(s)
    return out


# ---------------------------------------------------------------------------
# Body lint  (--check, step 1)
# ---------------------------------------------------------------------------

def _svg_ranges(html: str):
    """Return [(start,end)] char ranges covered by <svg>…</svg> (for id-skip)."""
    ranges = []
    for m in re.finditer(r'<svg\b', html, re.IGNORECASE):
        close = re.search(r'</svg\s*>', html[m.start():], re.IGNORECASE)
        end = m.start() + close.end() if close else len(html)
        ranges.append((m.start(), end))
    return ranges


def lint_body(body_text: str, allowed_classes, allowed_ids):
    """Flag any class= / id= token not in the manifest allowlist."""
    violations = []

    for m in re.finditer(r'\bclass="([^"]+)"', body_text):
        for cls in m.group(1).split():
            if cls not in allowed_classes:
                violations.append(("class", cls))

    svg = _svg_ranges(body_text)
    for m in re.finditer(r'\bid="([^"]+)"', body_text):
        idv = m.group(1)
        if any(a <= m.start() < b for a, b in svg):
            continue  # author-arbitrary SVG-local def id
        if idv in CHROME_IDS or idv in allowed_ids:
            continue
        violations.append(("id", idv))

    # de-dup, preserve order
    seen, uniq = set(), []
    for v in violations:
        if v not in seen:
            seen.add(v)
            uniq.append(v)
    return uniq


def selector_in_source(selector: str, sources: dict) -> bool:
    """True if the literal selector text appears in any named CSS source."""
    needle = re.escape(selector)
    # match the selector as a token (boundary before, then {/,/ /:/> etc. after)
    pat = re.compile(needle + r'(?![A-Za-z0-9_-])')
    for src in sources.values():
        if pat.search(src):
            return True
    return False


def base_coverage(styled_in):
    """Every own-token class/id must be styled in base.css or a shell <style>.

    Verifies BOTH the manifest claim (styled-in column) AND that the selector
    text actually resolves in the named source. Returns a list of failures.
    """
    base_css = read(ROOT / "base.css")
    src = {
        "base": base_css,
        "scroll": _shell_structural_css("scroll"),
        "slides": _shell_structural_css("slides"),
        "dashboard": _shell_structural_css("dashboard"),
        "cheatsheet": _shell_structural_css("cheatsheet"),
        "compare": _shell_structural_css("compare"),
        "diagram": _shell_structural_css("diagram"),
    }
    # A styled-in keyword may also name a vocabulary module whose contract/<mod>.css
    # sizes the primitive (injected wherever the module is allowlisted), e.g. `figures`.
    for mod_css in (ROOT / "contract").glob("*.css"):
        src[mod_css.stem] = read(mod_css)

    failures = []
    for sel, where in styled_in.items():
        if not where:
            failures.append(f"{sel}: manifest names no source (styled-in empty)")
            continue
        # the union of sources the manifest claims style this selector
        claimed = {k: src[k] for k in where if k in src}
        if not selector_in_source(sel, claimed):
            failures.append(
                f"{sel}: not found in claimed source(s) {sorted(where)} — naked or mis-attributed"
            )
    return failures


def _shell_structural_css(style: str) -> str:
    """Extract the LAST <style>…</style> block from a shell (structural CSS)."""
    html = read(ROOT / "shells" / style / "shell.html")
    blocks = re.findall(r"<style>(.*?)</style>", html, re.DOTALL)
    # block 0 is the {{CSS}} injection slot; the structural block is the last one
    return blocks[-1] if blocks else ""


# ---------------------------------------------------------------------------
# Contrast lint  (--lint-skins, step 3)
# ---------------------------------------------------------------------------

def _srgb_to_lin(c: float) -> float:
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb) -> float:
    r, g, b = (_srgb_to_lin(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(rgb1, rgb2) -> float:
    l1, l2 = relative_luminance(rgb1), relative_luminance(rgb2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def parse_hex(h: str):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        return None
    try:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return None


def mix_srgb(a, b, pct_a: float):
    """color-mix(in srgb, a pct_a%, b) — simple sRGB-channel mix."""
    f = pct_a / 100.0
    return tuple(round(a[i] * f + b[i] * (1 - f)) for i in range(3))


def _read_tokens(css: str) -> dict:
    """Pull :root custom-property hex values from a CSS string."""
    tokens = {}
    for m in re.finditer(r'(--[A-Za-z0-9-]+)\s*:\s*([^;}\n]+)', css):
        name, val = m.group(1), m.group(2).strip()
        rgb = parse_hex(val)
        if rgb:
            tokens[name] = rgb
    return tokens


def _resolve(tokens: dict, *names):
    for n in names:
        if n in tokens:
            return tokens[n]
    return None


def _band_accent_text_color(base_css: str, skin_css: str):
    """Find the color the skin (or base) applies to .band--accent label text.

    Returns the hex/var the most specific rule sets. Skins override base; we read
    skin first, then fall back to base's `.band--accent .eyebrow,.band--accent
    .kicker{color:…}` rule.
    """
    pat = re.compile(
        r'\.band--accent\s+\.(?:eyebrow|kicker)[^{]*\{[^}]*?color\s*:\s*([^;}\s]+)',
        re.DOTALL,
    )
    for css in (skin_css, base_css):
        m = pat.search(css)
        if m:
            return m.group(1).strip()
    return None


def _band_accent_fill(base_css: str, skin_css: str, tokens: dict):
    """Approximate the .band--accent fill (first gradient stop) for both palettes.

    base uses a var(--accent)->mix gradient; a light skin overrides it with two
    hex stops. The label text sits over the lighter region, but WCAG wants the
    worst case, so we take the FIRST gradient stop (the darker/saturated end on
    base, the pale end on warm-paper) as the dominant fill behind the label.
    """
    pat = re.compile(
        r'\.band--accent\s*\{[^}]*?background\s*:\s*([^;}]+)', re.DOTALL
    )
    for css in (skin_css, base_css):
        m = pat.search(css)
        if not m:
            continue
        decl = m.group(1)
        # first explicit hex in the gradient
        hexes = re.findall(r'#[0-9A-Fa-f]{3,6}', decl)
        if hexes:
            return parse_hex(hexes[0])
        # base: linear-gradient(135deg, var(--accent), color-mix(...))
        if "var(--accent)" in decl:
            return tokens.get("--accent")
    return None


def _resolve_color_value(val: str, tokens: dict):
    """Resolve a CSS color value (hex or var(--x)) to an rgb tuple."""
    val = val.strip()
    rgb = parse_hex(val)
    if rgb:
        return rgb
    m = re.match(r'var\((--[A-Za-z0-9-]+)\)', val)
    if m:
        return tokens.get(m.group(1))
    return None


def _copy_btn_text_color(base_css: str, skin_css: str):
    """The color #copy-btn sets on its label (skin overrides base)."""
    pat = re.compile(r'#copy-btn\s*\{[^}]*?color\s*:\s*([^;}\s]+)', re.DOTALL)
    for css in (skin_css, base_css):
        m = pat.search(css)
        if m:
            return m.group(1).strip()
    return None


# structural-sizing properties a skin must NEVER set (see skins/AUTHORING.md)
STRUCTURAL_SELECTOR_PAT = re.compile(
    r'(?<![A-Za-z0-9_#.-])'
    r'(section|\.slide|nav\.dots|footer|#progress|#overview|\.ov-[A-Za-z-]+|'
    r'\.reveal|mode-slides|mode-scroll)'
    r'(?![A-Za-z0-9_-])'
)
STRUCTURAL_VAR_PAT = re.compile(r'--(maxw|prose|pad)\b')
TYPE_SCALE_PAT = re.compile(
    r'(?<![A-Za-z0-9_#.-])(h1|h2|h3|p|\.lead)\b[^{}]*\{[^}]*\bfont-size\b'
)


def _strip_comments(css: str) -> str:
    return re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)


def check_skin_structural(skin_css: str):
    """Return a list of structural-sizing violations in a skin file."""
    css = _strip_comments(skin_css)
    issues = []

    for m in TYPE_SCALE_PAT.finditer(css):
        issues.append(f"sets type-scale font-size on `{m.group(1)}` (structural)")

    if STRUCTURAL_VAR_PAT.search(css):
        for m in STRUCTURAL_VAR_PAT.finditer(css):
            issues.append(f"sets container var `--{m.group(1)}` (structural)")

    # structural selectors with a body (i.e. the skin styles their layout)
    for m in re.finditer(r'([^{}]+)\{([^}]*)\}', css):
        selector = m.group(1)
        if STRUCTURAL_SELECTOR_PAT.search(selector):
            issues.append(f"styles structural selector `{selector.strip()}`")

    return issues


def lint_skins():
    """Audit every skins/*.css for contrast + structural-sizing leaks."""
    base_css = read(ROOT / "base.css")
    skin_paths = sorted((ROOT / "skins").glob("*.css"))
    if not skin_paths:
        sys.exit("error: no skins found in skins/")

    any_fail = False
    for sp in skin_paths:
        skin_css = read(sp)
        tokens = _read_tokens(base_css)          # base defaults
        tokens.update(_read_tokens(skin_css))    # skin overrides

        print(f"\n=== skins/{sp.name} ===")

        pairs = []  # (label, text_rgb, surface_rgb)

        fg = _resolve(tokens, "--fg")
        bg = _resolve(tokens, "--bg")
        if fg and bg:
            pairs.append(("body --fg on --bg", fg, bg))

        band_text = _band_accent_text_color(base_css, skin_css)
        band_fill = _band_accent_fill(base_css, skin_css, tokens)
        band_text_rgb = _resolve_color_value(band_text, tokens) if band_text else None
        if band_text_rgb and band_fill:
            pairs.append((".band--accent label vs band fill", band_text_rgb, band_fill))

        btn_text = _copy_btn_text_color(base_css, skin_css)
        btn_text_rgb = _resolve_color_value(btn_text, tokens) if btn_text else None
        accent = _resolve(tokens, "--accent")
        if btn_text_rgb and accent:
            pairs.append(("#copy-btn text vs --accent fill", btn_text_rgb, accent))

        for label, text_rgb, surf_rgb in pairs:
            ratio = contrast_ratio(text_rgb, surf_rgb)
            ok = ratio >= WCAG_AA_NORMAL
            mark = "PASS" if ok else "FAIL"
            if not ok:
                any_fail = True
            print(f"  [{mark}] {label}: {ratio:.2f}:1 "
                  f"(text {_hex(text_rgb)} on {_hex(surf_rgb)}, need ≥{WCAG_AA_NORMAL})")

        struct_issues = check_skin_structural(skin_css)
        if struct_issues:
            any_fail = True
            for s in struct_issues:
                print(f"  [FAIL] structural-sizing leak — {s}")
        else:
            print("  [PASS] no structural-sizing leaks")

    return not any_fail


def _hex(rgb):
    return "#%02x%02x%02x" % rgb


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def run_check(style: str, body_path: Path) -> bool:
    if not body_path.exists():
        sys.exit(f"error: missing body fragment: {body_path}")
    body_text = read(body_path)
    modules = style_modules(style)
    classes, ids, styled_in = parse_modules(modules)

    print(f"=== --check  style={style}  body={body_path} ===")
    print(f"modules: {', '.join(modules)}")
    print(f"manifest allowlist: {len(classes)} classes, {len(ids)} ids, "
          f"{len(styled_in)} own-token rows")

    ok = True

    # step 1 — body lint
    violations = lint_body(body_text, classes, ids)
    if violations:
        ok = False
        print(f"  [FAIL] body lint: {len(violations)} unknown token(s):")
        for kind, name in violations:
            print(f"           unknown {kind}=\"{name}\"")
    else:
        print("  [PASS] body lint: every class= / id= is allowlisted")

    # step 2 — base coverage
    failures = base_coverage(styled_in)
    if failures:
        ok = False
        print(f"  [FAIL] base coverage: {len(failures)} unstyled token(s):")
        for f in failures:
            print(f"           {f}")
    else:
        print("  [PASS] base coverage: every manifest token is styled in "
              "base.css or a shell")

    return ok


GUIDE_HELP = """\
# present · authoring guide — STYLE={style}

This is EVERYTHING you need to author a {style} page in fast mode, in one place.
Write ONLY a body fragment (the structure-specific content the shell does not
provide), then run the build command at the bottom — build.py assembles the
shell, base.css, the skin, and the engine around it. Do NOT open the other skill
files or browse the directory: the composition rules, the full {style} vocabulary
(your class allowlist), the worked examples, the skins, and the commands are all
inline below. The worked examples carry the exact markup to copy — including the
full inline-SVG skeletons; base.css only COLORS the SVGs and carries no geometry,
so never read it to learn structure."""


def run_guide(style: str) -> None:
    """Print the complete fast-authoring brief for one STYLE to stdout.

    A single source-of-truth assembly: the shared rules (contract.md), the
    style's allowlisted vocabulary modules, the available skins, the worked
    example fragments (full markup incl. SVG skeletons), and the build commands.
    The author runs this once and works from its output — no file browsing.
    """
    def doc(p: Path) -> str:
        return read(p).replace("{{SKILL_DIR}}", str(ROOT))

    parts = [GUIDE_HELP.format(style=style), doc(ROOT / "contract.md")]
    for m in style_modules(style):
        parts.append(doc(ROOT / "contract" / f"{m}.md"))

    skins = sorted(p.stem for p in (ROOT / "skins").glob("*.css"))
    parts.append("# Skins\n\nPin one with `--skin <name>`, or omit `--skin` for a "
                 "random curated skin:\n" + "".join(f"- {s}\n" for s in skins))

    examples = sorted((ROOT / "shells" / style / "examples").glob("*.body.html"))
    if examples:
        ex = ["# Worked examples — real body fragments for this STYLE",
              "Copy/adapt the markup; each assembles or `--check`s directly. Inline-SVG "
              "primitives show their full skeleton here (base.css only styles them)."]
        for e in examples:
            ex.append(f"## {e.name}\n\n```html\n{read(e).rstrip()}\n```")
        parts.append("\n\n".join(ex))

    parts.append(
        "# Build\n\n```\n"
        f"python3 {ROOT}/build.py --check --style {style} --body <fragment>   # pre-flight lint\n"
        f"python3 {ROOT}/build.py --style {style} --body <fragment> [--skin <name>] [--out <path>]\n"
        "```\nWrite the fragment to /tmp, `--check` it, build, then open the output "
        "(`open <file>` on macOS) unless the user gave a location.")

    print("\n\n---\n\n".join(parts))


def main():
    ap = argparse.ArgumentParser(description="Assemble + verify a present page from parts.")
    ap.add_argument("--style", choices=["scroll", "slides", "dashboard", "cheatsheet", "compare", "diagram"])
    ap.add_argument("--body", help="path to the body fragment")
    ap.add_argument("--skin", help="skin name (omit to pick a random skin)")
    ap.add_argument("--seed", type=int, help="pin the RNG for a reproducible random skin")
    ap.add_argument("--out", help="output path (default /tmp/present-<style>-<skin>.html)")
    ap.add_argument("--check", action="store_true",
                    help="run body-lint + base-coverage (needs --style and --body)")
    ap.add_argument("--lint-skins", action="store_true",
                    help="audit every skins/*.css for contrast + structural sizing")
    ap.add_argument("--guide", action="store_true",
                    help="print the full fast-authoring brief for --style and exit")
    args = ap.parse_args()

    if args.lint_skins:
        sys.exit(0 if lint_skins() else 1)

    if args.guide:
        if not args.style:
            ap.error("--guide requires --style")
        run_guide(args.style)
        sys.exit(0)

    if args.check:
        if not args.style or not args.body:
            ap.error("--check requires --style and --body")
        sys.exit(0 if run_check(args.style, Path(args.body)) else 1)

    # default: assemble
    if not args.style or not args.body:
        ap.error("assembly requires --style and --body")
    body_path = Path(args.body)
    if not body_path.exists():
        sys.exit(f"error: missing body fragment: {body_path}")
    skin = args.skin or pick_skin(args.seed)
    skin_path = ROOT / "skins" / f"{skin}.css"
    if not skin_path.exists():
        sys.exit(f"error: unknown skin '{skin}' (no {skin_path})")

    html = assemble(args.style, read(body_path), skin)
    out = Path(args.out) if args.out else Path(f"/tmp/present-{args.style}-{skin}.html")
    out.write_text(html, encoding="utf-8")
    print(f"skin: {skin}")
    print(f"out:  {out}")


if __name__ == "__main__":
    main()
