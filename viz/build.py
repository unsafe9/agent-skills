#!/usr/bin/env python3
"""Assemble + verify a single self-contained offline viz page from YAML data.

The model writes ONLY `blocks:` data (a list of typed blocks). This script
validates it against schema.yaml, renders each block to a <section> via its
components/<type>.py, and assembles the shell + base.css + a random skin +
space.css + the per-component CSS into one offline HTML file. No DOM, SVG
coordinates, or page chrome ever enter model output — that is the token lever.

Cascade is base -> skin -> space -> component-structural -> shell-structural:
  <head> emits <style>{{CSS}}</style> = base.css, skins/<name>.css, space.css,
  then each appearing component's components/<type>.css, ABOVE the shell's literal
  structural <style>. So the skin :root overrides base tokens; space.css sets the
  shared gap/pad ladder; component + shell structural sizing win over the skin and
  are immune to reskinning.

schema.yaml is the single source of truth: it drives --check (validation) and the
coverage guard (declared block types == component module stems), and doubles as the
authoring reference agents read.

Usage:
  build.py --data page.yaml [--skin warm-paper] [--seed 7] [--out path]
  build.py --check --data page.yaml      # validation + coverage only, exit 0/1
"""
import argparse
import importlib.util
import random
import re
import sys
from difflib import get_close_matches
from pathlib import Path

def _load_yaml():
    """Import pyyaml, self-installing it on first run if absent.

    The skill carries its own one dependency: drop viz/ anywhere and build.py
    bootstraps pyyaml into the running interpreter rather than relying on an
    external installer. No-op once installed."""
    try:
        import yaml
        return yaml
    except ImportError:
        pass
    import subprocess
    import importlib
    sys.stderr.write("viz: pyyaml not found — installing it now (one time)…\n")
    for extra in ([], ["--user"]):
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--quiet",
                            *extra, "pyyaml"], check=True)
        except Exception:
            continue
        importlib.invalidate_caches()
        try:
            import site
            usp = site.getusersitepackages()
            if usp and usp not in sys.path:
                sys.path.append(usp)
        except Exception:
            pass
        try:
            return importlib.import_module("yaml")
        except ImportError:
            continue
    sys.exit("viz needs pyyaml and auto-install failed. Run:\n"
             f"  {sys.executable} -m pip install pyyaml")


yaml = _load_yaml()

ROOT = Path(__file__).resolve().parent

PLACEHOLDERS = ("{{CSS}}", "{{JS}}", "{{TITLE}}", "{{BODY}}")

# field-spec keys the validator understands (anything else in a spec is a typo)
SPEC_KEYS = {"required", "kind", "enum", "item", "desc"}


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# schema + components
# ---------------------------------------------------------------------------

def load_schema() -> dict:
    path = ROOT / "schema.yaml"
    if not path.exists():
        sys.exit(f"error: missing schema: {path}")
    return yaml.safe_load(read(path))


def component_stems() -> list:
    """Discover components/*.py renderers (leading-underscore files are helpers)."""
    return sorted(
        p.stem for p in (ROOT / "components").glob("*.py")
        if not p.stem.startswith("_")
    )


def load_renderer(type_name: str):
    """Import components/<type>.py and return its render() callable."""
    path = ROOT / "components" / f"{type_name}.py"
    spec = importlib.util.spec_from_file_location(f"viz_component_{type_name}", path)
    mod = importlib.util.module_from_spec(spec)
    # components import sibling helpers (`from _util import …`); make components/ importable
    comp_dir = str(ROOT / "components")
    if comp_dir not in sys.path:
        sys.path.insert(0, comp_dir)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "render"):
        sys.exit(f"error: components/{type_name}.py has no render(block) function")
    return mod.render


def check_coverage(schema: dict) -> list:
    """Anti-drift guard: schema block types must match component module stems."""
    declared = set(schema.get("blocks", {}))
    rendered = set(component_stems())
    errs = []
    for t in sorted(declared - rendered):
        errs.append(f"block type '{t}' declared in schema.yaml but has no components/{t}.py")
    for t in sorted(rendered - declared):
        errs.append(f"components/{t}.py exists but no '{t}' block declared in schema.yaml")
    return errs


# ---------------------------------------------------------------------------
# validation  (generic, driven by schema.yaml — not hardcoded per type)
# ---------------------------------------------------------------------------

def _suggest(name, known) -> str:
    m = get_close_matches(str(name), list(known), n=1, cutoff=0.6)
    return f" — did you mean '{m[0]}'?" if m else ""


def _validate_fields(fields_spec: dict, data: dict, loc: str, errs: list,
                     block_specs: dict = None):
    """Validate a {fieldname: spec} map against a data dict. Recurses one level
    into list `item` shapes, and into nested blocks for `kind: blocks` fields
    (dispatching each child by its type via `block_specs`). `loc` is the human
    path prefix for messages."""
    if not isinstance(data, dict):
        errs.append(f"{loc}: expected a map, got {type(data).__name__}")
        return
    known = set(fields_spec)
    for fname, spec in fields_spec.items():
        spec = spec or {}
        present = fname in data
        if spec.get("required") and not present:
            errs.append(f"{loc}: missing required field '{fname}'")
            continue
        if not present:
            continue
        value = data[fname]
        kind = spec.get("kind", "scalar")
        enum = spec.get("enum")
        if kind == "list":
            if not isinstance(value, list):
                errs.append(f"{loc}: field '{fname}' must be a list")
                continue
            item_spec = spec.get("item")
            if item_spec:
                for i, el in enumerate(value):
                    _validate_fields(item_spec, el, f"{loc} {fname}[{i}]", errs)
        elif kind == "blocks":
            if not isinstance(value, list):
                errs.append(f"{loc}: field '{fname}' must be a list of blocks")
                continue
            if block_specs is not None:
                for i, el in enumerate(value):
                    _validate_block(el, f"{loc} {fname}[{i}]", block_specs, errs)
        elif kind == "map":
            if not isinstance(value, dict):
                errs.append(f"{loc}: field '{fname}' must be a map")
        else:  # scalar
            if enum and value not in enum:
                errs.append(f"{loc}: field '{fname}'='{value}' not in {enum}")
    for fname in data:
        if fname not in known:
            errs.append(f"{loc}: unknown field '{fname}'{_suggest(fname, known)}")


def _validate_block(block, loc: str, block_specs: dict, errs: list):
    """Validate one typed block: dispatch by `type` to its field spec, then check
    its fields (recursing into nested `kind: blocks` children)."""
    known_types = set(block_specs)
    if not isinstance(block, dict):
        errs.append(f"{loc}: each block must be a map with a 'type'")
        return
    btype = block.get("type")
    if btype is None:
        errs.append(f"{loc}: missing 'type'")
        return
    if btype not in known_types:
        errs.append(f"{loc}: unknown block type '{btype}'{_suggest(btype, known_types)}")
        return
    loc = f"{loc} ({btype})"
    fields_spec = dict(block_specs[btype].get("fields", {}))
    # `nav` and `type` are accepted on every block (type is the discriminant, nav
    # is the common optional side-rail label)
    fields_spec.setdefault("nav", {"desc": "side-rail dot label"})
    payload = {k: v for k, v in block.items() if k != "type"}
    _validate_fields(fields_spec, payload, loc, errs, block_specs)


def validate(schema: dict, page: dict) -> list:
    """Validate a parsed page dict against schema.yaml. Returns error strings."""
    errs = []
    if not isinstance(page, dict):
        return ["page: top-level document must be a map with 'title' and 'blocks'"]

    # page-level fields (title/skin/blocks), reusing the field-spec validator
    page_spec = schema.get("page", {})
    page_data = {k: page[k] for k in page if k != "blocks"}
    flat_spec = {k: v for k, v in page_spec.items() if k != "blocks"}
    _validate_fields(flat_spec, page_data, "page", errs)

    blocks = page.get("blocks")
    if not isinstance(blocks, list):
        errs.append("page: 'blocks' is required and must be a list")
        return errs

    block_specs = schema.get("blocks", {})
    for i, block in enumerate(blocks):
        _validate_block(block, f"block[{i}]", block_specs, errs)
    return errs


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------

def pick_skin(seed):
    skins = sorted(p.stem for p in (ROOT / "skins").glob("*.css"))
    if not skins:
        sys.exit("error: no skins found in skins/")
    return random.Random(seed).choice(skins)


def substitute_once(html: str, token: str, value: str) -> str:
    n = html.count(token)
    if n != 1:
        sys.exit(f"error: placeholder {token} occurs {n}x in scroll.shell.html "
                 f"(expected exactly 1)")
    return html.replace(token, value)


def _collect_types(blocks, acc=None):
    """All block types appearing in the page, recursing into container blocks
    (group children) so their component CSS is tree-shaken in too."""
    acc = [] if acc is None else acc
    for b in blocks:
        if not isinstance(b, dict):
            continue
        t = b.get("type")
        if t and t not in acc:
            acc.append(t)
        if isinstance(b.get("blocks"), list):
            _collect_types(b["blocks"], acc)
    return acc


def assemble(page: dict, skin: str) -> str:
    shell_path = ROOT / "scroll.shell.html"
    base_path = ROOT / "base.css"
    skin_path = ROOT / "skins" / f"{skin}.css"
    space_path = ROOT / "space.css"
    for p in (shell_path, base_path, skin_path, space_path):
        if not p.exists():
            sys.exit(f"error: missing required input: {p}")

    blocks = page["blocks"]
    used_types = _collect_types(blocks)

    # CSS cascade: base -> skin -> space -> per-component (only for types in use)
    css = read(base_path).rstrip("\n") + "\n\n" + read(skin_path)
    css += "\n\n" + read(space_path)
    for t in used_types:
        cpath = ROOT / "components" / f"{t}.css"
        if cpath.exists():
            css += "\n\n" + read(cpath)

    js = read(ROOT / "engine.js").rstrip("\n") + "\n\n" + read(ROOT / "composer.js")

    # render: an auto hero from page metadata (eyebrow/title/lead), then each block's <section>
    title = str(page["title"])
    from html import escape
    hero = []
    if page.get("eyebrow"):
        hero.append(f'<div class="eyebrow">{escape(str(page["eyebrow"]), quote=True)}</div>')
    hero.append(f'<h1>{escape(title, quote=True)}</h1>')
    if page.get("lead"):
        hero.append(f'<p class="lead">{escape(str(page["lead"]), quote=True)}</p>')
    sections = ['<section class="hero"><div class="wrap reveal">'
                + "".join(hero) + '</div></section>']
    for b in blocks:
        sections.append(load_renderer(b["type"])(b))

    # if any block is a decision, append the composer section so composer.js activates
    if "decision" in used_types:
        comp = page.get("composer", {}) or {}
        lead = escape(str(comp.get("lead", "") or ""), quote=True)
        tail = escape(str(comp.get("tail", "") or ""), quote=True)
        sections.append(
            f'<section id="composer" data-lead="{lead}" data-tail="{tail}">'
            '<div class="wrap"><pre id="prompt-preview"></pre>'
            '<button id="copy-btn">Copy</button></div></section>'
        )

    body = "\n".join(sections)

    html = read(shell_path)
    html = substitute_once(html, "{{CSS}}", css)
    html = substitute_once(html, "{{JS}}", js)
    html = substitute_once(html, "{{TITLE}}", escape(title, quote=True))
    html = substitute_once(html, "{{BODY}}", body)

    # ASSERT: assembly is complete and loads NO external resources. The guard
    # must NOT false-positive on code/prose that merely *mentions* <link>,
    # @import, or url(...) — coding content is full of those as text. Body text
    # is HTML-escaped (< → &lt;), so a literal tag can only be real markup, and
    # url()/@import are only meaningful inside our assembled <style>. Navigation
    # links (<a href="https://…">) and URLs shown as text/code stay fine.
    if "{{" in html:
        leftover = html[html.index("{{"):html.index("{{") + 40]
        sys.exit(f"error: unsubstituted placeholder remains: {leftover!r}")
    # (a) CSS-level: external @import / url() inside the assembled stylesheet only
    if "@import" in css.lower() or re.search(r'url\(\s*["\']?(?:https?:)?//', css, re.I):
        sys.exit("error: external resource in CSS (@import or url(...))")
    # (b) markup-level: <link> tags and external src/data on resource elements.
    #     Body text is escaped, so these match only real injected markup.
    if "<link" in html.lower():
        sys.exit("error: <link> external resource tag found")
    for m in re.finditer(
        r'<(?:script|img|iframe|source|audio|video|track|object|embed)\b[^>]*?'
        r'\b(?:src|data)\s*=\s*["\']([^"\']+)', html, re.I):
        u = m.group(1)
        if not u.startswith("data:") and re.match(r'(?:https?:)?//', u):
            sys.exit(f"error: external resource src found: {u!r}")
    return html


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def load_page(data_path: Path) -> dict:
    if not data_path.exists():
        sys.exit(f"error: missing data file: {data_path}")
    try:
        return yaml.safe_load(read(data_path))
    except yaml.YAMLError as e:
        sys.exit(f"error: invalid YAML in {data_path}: {e}")


def run_check(schema: dict, page: dict, data_path: Path) -> bool:
    print(f"=== --check  data={data_path} ===")
    ok = True

    cov = check_coverage(schema)
    if cov:
        ok = False
        print(f"  [FAIL] coverage: {len(cov)} drift issue(s):")
        for c in cov:
            print(f"           {c}")
    else:
        print("  [PASS] coverage: schema block types == component renderers")

    errs = validate(schema, page)
    if errs:
        ok = False
        print(f"  [FAIL] validation: {len(errs)} error(s):")
        for e in errs:
            print(f"           {e}")
    else:
        print("  [PASS] validation: every block is well-formed")
    return ok


def main():
    ap = argparse.ArgumentParser(description="Assemble + verify a viz page from YAML data.")
    ap.add_argument("--data", help="path to the page YAML")
    ap.add_argument("--skin", help="skin name (omit to pick a random skin)")
    ap.add_argument("--seed", type=int, help="pin the RNG for a reproducible random skin")
    ap.add_argument("--out", help="output path (default /tmp/viz-<skin>.html)")
    ap.add_argument("--check", action="store_true",
                    help="run validation + coverage only (needs --data)")
    args = ap.parse_args()

    schema = load_schema()

    if not args.data:
        ap.error("--data is required")
    data_path = Path(args.data)
    page = load_page(data_path)

    if args.check:
        sys.exit(0 if run_check(schema, page, data_path) else 1)

    # default: validate, then assemble
    cov = check_coverage(schema)
    errs = validate(schema, page)
    if cov or errs:
        print("error: page is invalid — run --check for details", file=sys.stderr)
        for m in cov + errs:
            print(f"  {m}", file=sys.stderr)
        sys.exit(1)

    # precedence: --skin flag > page-level `skin:` field > random
    skin = args.skin or page.get("skin") or pick_skin(args.seed)
    skin_path = ROOT / "skins" / f"{skin}.css"
    if not skin_path.exists():
        sys.exit(f"error: unknown skin '{skin}' (no {skin_path})")

    html = assemble(page, skin)
    out = Path(args.out) if args.out else Path(f"/tmp/viz-{skin}.html")
    out.write_text(html, encoding="utf-8")
    print(f"skin: {skin}")
    print(f"out:  {out}")


if __name__ == "__main__":
    main()
