# Interaction Design and Performance

Alfred lives on immediacy: the user types and watches results change in the same
window. Design every workflow so the next step is visible LIVE rather than
discovered after pressing Enter.

## Live-first flow design

- Prefer one Script Filter that computes results while the user types over chains of
  typed-input objects. Chaining inputs (Keyword → List Filter, input → input in
  general) costs an Enter per hop — and the argument passed into the next input
  lands in its query box, where it FILTERS that input's items: the user sees an
  empty-looking list until they manually clear the text (observed behavior).
- When the workflow transforms its input (encode, hash, convert, format…), emit one
  item per operation and put the COMPUTED RESULT in that item's subtitle — e.g.
  title "URL Encode", subtitle `hello%20world`. The user compares every outcome at a
  glance; Enter only delivers a value they have already seen.
- Reserve multi-step flows for genuinely branching interactions (pick a target, then
  pick an action on it) — and give the second step live previews too.
- When the result is too rich for a row + subtitle — a rendered Markdown readout, a
  multi-line answer, an image grid, a PDF — escalate to a User Interface view (Text
  View, Grid View, Image View, PDF View; see objects.md) instead of cramming it into
  Script Filter subtitles or flashing it through Large Type. A Text View is the right
  home for chat/answer/log surfaces; a Grid View for visual pickers.

## Forgiving input

Never make the user pre-compute or re-format what the script can derive. Three habits:

- **Accept every reasonable notation of a value.** Durations `90`/`5m`/`1h30m`;
  dates `tomorrow 3pm`/`+2d`; sizes `10mb`; colors `#ff8800`/`orange`; numbers
  `1,000`/`15%`; URLs without scheme; `~` and relative paths; toggles `on`/`yes`/`1`.
  Bare numbers get a sensible default unit; case and trailing junk are tolerated;
  args with distinguishable shapes work in either order (`30m tea` = `tea 30m`).
- **Accept a target in whatever form the user has at hand** — name, id, or URL
  (`JIRA-123` or its full link, a PID or a process name, a SHA prefix) — and resolve
  them to the same thing. Widen choice matching with the item `match` field so
  abbreviations hit (`enc` → URL Encode).
- **Empty input falls back to the obvious source** — clipboard contents, current
  selection, or a sensible default — when that is what the user almost certainly
  means.

Reflect the parse back (live-first applied to input): echo the canonical
interpretation in the subtitle while typing ("1h 30m — ends 15:42"); unparseable
input returns a `valid: false` item stating what is expected — never a silent empty
list or an error discovered only after Enter.

## Item icons

Icons make lists scannable; a column of identical generic icons wastes the canvas
Alfred gives you. In priority order:

1. **Native, programmatic** — when the target itself has an icon, point at it:
   `"icon": {"type": "fileicon", "path": "/Applications/Safari.app"}` renders that
   file's own icon at zero cost. Processes → resolve the PID to its `.app` bundle
   path; files/folders → `fileicon` on the path; file kinds → `"type": "filetype"`
   with a UTI.
2. **Remote, cached** — favicons, avatars, cover art: download once into
   `$alfred_workflow_cache`, reference the cached path thereafter. Never fetch
   during a keystroke (see Performance).
3. **Generated** — abstract choices with no natural icon (operations, modes):
   generate a small icon set the same way as the workflow icon (packaging.md §
   Icon), one 256–512px PNG per item in the workflow folder (`icons/<id>.png`),
   referenced by relative path.

## Performance

The Script Filter run-behaviour rules (objects.md) are one instance of a broader
law: nothing the user is waiting on may block on network or repeated work.

- **Render first, fetch later.** The first output must come from local data and
  cached assets (placeholder icons while the cache is cold). Kick off missing-asset
  fetches in the background and let `cache.loosereload` or a one-shot `rerun` pick
  them up.
- **Cache remote assets and expensive results** under `$alfred_workflow_cache`
  (volatile, per-machine) or `$alfred_workflow_data` (persistent), keyed by target
  with a TTL — never re-download what is already on disk.
- **Fetch in parallel, never sequentially.** Twenty favicons fetched serially is
  twenty times slower than a capped parallel fetch (`xargs -P8`, concurrent
  requests). Cap concurrency and time out fast.
- **`rerun` is a cost, not a decoration.** Every tick re-executes the whole script
  for as long as the filter is open. Enable it only when the display must change
  while the user watches, and keep the script cheap.
- **Keep row order stable between reruns.** Re-sorting live data each tick shuffles
  rows under the user's cursor right as they try to act. Sort by stable identity
  (name, id) rather than by the fluctuating metric — or freeze the order from the
  first run — and let only subtitles (numbers, status) update.
- **View objects obey the same law.** A Grid View's remote image tiles must be cached
  and parallel-fetched with placeholders while cold — identical to item icons above;
  never fetch them while the user filters. A Text View driven by a script or `rerun`
  re-runs that script on every update, so keep it cheap and cache anything expensive.
- **Synchronous steps block the stream — keep them off live paths.** Run Shortcut and
  Automation Task execute and wait (Run Shortcut also pays the Shortcuts app's
  cold-start), and Delay pauses by design. Put them after the user has acted
  (post-Enter), never inside a Script Filter preview or a rerun loop the user watches.
- **A File Filter scans the disk on every keystroke.** A broad scope or a long file-type
  list makes each search do more work; narrow both so results stay instant.
