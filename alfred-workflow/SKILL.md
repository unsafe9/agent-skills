---
name: alfred-workflow
description: Author Alfred 5 workflows as code by writing the native info.plist XML — object graph, connections, canvas layout (uidata), user configuration — then validating, packaging into .alfredworkflow, and installing. Use whenever the user wants to create, modify, lay out, debug, package, or install an Alfred workflow or macOS launcher automation, mentions .alfredworkflow, Script Filter, Alfred keyword/hotkey/external trigger, or says 'build an Alfred workflow', 'add an Alfred keyword'. Trigger even when the user only describes the desired launcher behavior without naming Alfred internals.
---

# Alfred Workflow Authoring

Build Alfred workflows the way Alfred's GUI editor would: a native object graph in
`info.plist`, not a single mega-script. A native graph is what the user later sees and
edits on the canvas, gets per-object debugging, and survives GUI round-trips.

Requires macOS with Alfred 5 + Powerpack. If `/Applications/Alfred 5.app` is missing,
stop and tell the user instead of building blind.

## Core model

- A workflow IS its `info.plist` (Apple XML plist). A `.alfredworkflow` file is a ZIP
  of the workflow folder's contents with `info.plist` at the archive root.
- Four coupled top-level structures must stay consistent: `objects` (nodes),
  `connections` (edges, keyed by source uid), `uidata` (canvas positions, keyed by
  uid), `userconfigurationconfig` (user-facing settings).
- Prefer native objects (Conditional, Arg and Vars, Automation Task, List Filter,
  Text View, Notification, …) over folding logic into one big Run Script. Scripts are
  for actual logic only. For rich output (rendered Markdown, image grids, PDFs) reach
  for a User Interface view rather than a Script Filter row — see the User Interface
  section in `references/objects-catalog.md`.
- Never assemble plist XML by string concatenation — `&`, `<`, `>` inside inline
  scripts silently corrupt the file. Start from `{{SKILL_DIR}}/assets/skeleton.plist`
  or generate/edit with `python3` + `plistlib`.

## Authoring loop

1. **Design the graph first**: triggers/inputs → utilities → actions → outputs. Note
   modifier-key alternatives, conditional branches, and every value a user should be
   able to change (keyword, API key, paths → User Configuration). Design for live
   feedback: one Script Filter whose items preview the outcome (with real item
   icons) beats Enter-chained input objects — read
   `references/ux-and-performance.md` before settling the flow.
2. **Scaffold**: copy `{{SKILL_DIR}}/assets/skeleton.plist` into a working folder as
   `info.plist`, or build with `plistlib`. Real-world reference plists live in
   `{{SKILL_DIR}}/references/examples/`.
3. **Write objects** per `references/objects.md`. Generate a fresh UPPERCASE UUID per
   object (`uuidgen` already outputs uppercase).
4. **Wire connections** (same file, "Connections" section) — including conditional
   `sourceoutputuid` routing and modifier-key edges.
5. **Lay out the canvas** per `references/layout.md` so the graph reads left→right
   and nothing overlaps.
6. **Validate**: `python3 {{SKILL_DIR}}/scripts/validate.py <workflow-dir>`. Fix every
   error; fix warnings too unless you can say why one is intentional.
7. **Pack**: `{{SKILL_DIR}}/scripts/pack.sh <workflow-dir> [out.alfredworkflow]`.
   If there is no `icon.png` yet, create one first — see the Icon section of
   `references/packaging.md` (generate via an available image-generation skill).
8. **Install and verify** per `references/packaging.md`, then sanity-check in Alfred's
   debugger and on the canvas.

## Critical rules

These are the silent-failure points — Alfred won't raise an error, the workflow just
misbehaves:

- Object `uid`s are UPPERCASE UUIDs and must be unique. `connections` and `uidata`
  reference objects only by these uids.
- The connection key for "close Alfred window" is spelled **`vitoclose`** — Alfred's
  own historical typo. A correctly-spelled `vetoclose` is silently ignored.
- Script `config.type` integers: use only verified values — `0` bash, `2` ruby, `7`
  JXA (`osascript -l JavaScript`), `8` External Script, `11` zsh (modern default;
  Alfred's own automation tasks use 11). An external `scriptfile` runs ONLY with
  `type` 8 — any other type silently runs the inline `script` instead. For python3
  or anything else, use `scriptfile` + type 8, or a one-line shell shim
  (`/usr/bin/env python3 script.py "$1"`) under type 0/11.
- Pass input as argv (`scriptargtype` = 1), not `{query}` (= 0): argv needs no
  escaping. Keep both `script` and `scriptfile` keys present; the unused one is an
  empty string.
- Non-ASCII query/argv text can arrive NFD-decomposed (macOS input methods, file
  paths), so Korean and accented matches against NFC data silently miss. Normalize
  to NFC before comparing or searching — e.g. `unicodedata.normalize('NFC', text)`
  in python3.
- A Conditional's branch routing lives in the connection's `sourceoutputuid`, which
  must equal the `uid` inside the matching `config.conditions[]` entry. The edge
  without `sourceoutputuid` is the else branch.
- Anything user-tunable (keywords, API keys, paths, options) goes in
  `userconfigurationconfig` and is referenced as `{var:name}` in object fields —
  never hardcoded, never in plain `variables` (those export with the file; secrets
  would leak).
- In scripts: stdout is the result stream, stderr goes to Alfred's debugger. PATH is
  `/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin` and rc files are
  not loaded. Use paths relative to the workflow folder for bundled files.

## References

| Read | When |
|---|---|
| `references/objects.md` | Writing any object or connection — the full type-string index, the mechanics (envelope, connections, script config), and the common-object config schemas |
| `references/objects-catalog.md` | Config schemas for the specialized objects the index routes here — User Interface views, Automations extras, and the less-common triggers/inputs/actions/utilities/outputs |
| `references/layout.md` | Assigning `uidata` positions, notes, colors |
| `references/script-filter-json.md` | Writing a Script Filter's script output |
| `references/ux-and-performance.md` | Designing the interaction — live previews, forgiving input formats, item icons, caching, parallel fetch, rerun stability |
| `references/config-and-variables.md` | User Configuration fields, variable scopes, runtime env vars |
| `references/packaging.md` | Packing, installing, reloading, debugging, distributing |
| `references/examples/` | Reference info.plist files — official/popular workflow exports plus one complete validated example — copy shapes from here when unsure |

Every object's exact `type` string is in the type index at the top of
`references/objects.md` — look it up there, never guess (a wrong string is silently
dropped). When an object's *config* shape is not catalogued either, don't guess key
names: find a real instance — in `references/examples/`, an installed workflow under
Alfred's preferences folder, or an `alfredapp` org workflow on GitHub — and copy its
shape.
