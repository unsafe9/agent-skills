# Mode: fast (the default)

The token/latency lever, and what you use for almost everything. You write **only** a body fragment in
the fixed vocabulary plus a skin pick; `build.py` mechanically assembles the shell + `base.css` + skin +
engine into one offline file. The CSS scaffold, JS engine, and page chrome never enter your output — that
is the whole point. It reads well and costs a fraction. Move off this path only when craft is the
explicit point (then `modes/creative.md` / `modes/presentation.md`).

## Workflow (step by step)

1. **Outline first.** Decide the sequence: chunk the answer so each part carries one idea, and write each
   headline as the takeaway (a full claim, not a label). Lead with the answer. This is where reading
   comfort is won or lost — before any HTML.
2. **Pick the STYLE** (scroll unless the shape says otherwise), then run
   `python3 {{SKILL_DIR}}/build.py --guide --style <style>`. It prints the whole brief in one shot — the
   composition rules, your STYLE's full vocabulary (the class allowlist), the fragment root to write,
   worked examples to copy, the skins, and the build command. Work from that output; don't open the
   contract or example files yourself.
3. **Write ONLY a body fragment** to `/tmp` (e.g. `/tmp/present-<slug>.body.html`) — the
   structure-specific content the shell does NOT provide. The guide's `## Composing <style>` note names
   the exact fragment root and what it must contain (e.g. scroll = `<main>` of `<section data-nav>` blocks
   + a bottom `#composer`; diagram = `<main class="canvas">` of a `.fig-head` + `.stage` figures). Copy an
   inline-SVG primitive's full skeleton from a worked example — base.css only colors it, so there is no
   geometry to read there. Do NOT emit `<head>`, `<style>`, `<script>`, base CSS, the engine, or page
   chrome — `build.py` injects all of it.
4. **Assemble:** `python3 {{SKILL_DIR}}/build.py --style <s> --body <file> [--skin <name>] [--out path]`.
   Omit `--skin` to get a random curated skin; pin one with `--skin <name>` (skins live in
   `{{SKILL_DIR}}/skins/`). The script fails loudly if any placeholder is left or any external resource
   leaks. Optionally pre-flight with `--check --style <s> --body <file>` (body-lint + base coverage).
5. **Open** the output (`open <file>` on macOS) unless the user gave a location.
6. **Leave a short pointer in chat, not the content** — a couple of lines: what it covers and the path.
   Re-dumping the full answer defeats the purpose.

## Make decisions actionable

When the answer hinges on the user's input, end a scroll/slides page with each open question as
selectable `.option`s (mark your lean `.pick`), a free-text box where useful, and a `#composer` that
assembles the picks into a short next-step prompt **in the user's own casual voice** — so they read →
choose → copy → paste back. (Dashboard has none; compare carries its own decision + copy-out.)
