# Script Filter JSON Protocol

A Script Filter's script prints this JSON to stdout; Alfred renders `items` as live
results. Anything on stderr goes to the debugger instead — log there.

## Root object

```json
{
  "items": [],
  "variables": {"key": "value"},
  "rerun": 1.0,
  "cache": {"seconds": 300, "loosereload": true},
  "skipknowledge": true
}
```

| Field | Notes |
|---|---|
| `items` | Required. |
| `variables` | Stream variables passed downstream — and back into the script on `rerun`, which is how you keep state across reruns. |
| `rerun` | 0.1–5.0 s. Alfred re-invokes the script while the filter stays open — for live/polling UIs. Every tick re-runs the whole script, and re-sorted output shuffles rows under the user's cursor — keep order stable between ticks and let only subtitles update (`ux-and-performance.md`). |
| `cache.seconds` | 5–86400. Alfred replays the last output instead of running the script. Use for anything network-backed. |
| `cache.loosereload` | `true` = show stale cache instantly, refresh in background. Almost always what you want with `cache`. |
| `skipknowledge` | `true` = preserve item order exactly (Alfred's learned ranking off). Use for ordered/computed results. |

## Item object

```json
{
  "uid": "stable-id",
  "title": "Shown big",
  "subtitle": "Shown small",
  "arg": "passed downstream",
  "match": "alternative filter text",
  "autocomplete": "tab-completion text",
  "valid": true,
  "type": "default",
  "icon": {"path": "icon.png"},
  "mods": {
    "alt": {"subtitle": "⌥ does something else", "arg": "alt-value"},
    "cmd+shift": {"subtitle": "combo", "arg": "other"}
  },
  "text": {"copy": "⌘C text", "largetype": "⌘L text"},
  "quicklookurl": "https://example.com",
  "variables": {"picked": "1"}
}
```

| Field | Notes |
|---|---|
| `title` | Required; everything else optional. |
| `uid` | Feeds Alfred's frequency learning; same uid = same item across runs. Omit it (or set root `skipknowledge`) to keep your own order. |
| `arg` | String or array (array passes multiple args downstream). The value `{query}` refers to downstream. |
| `valid` | `false` = Enter does nothing; pair with `autocomplete` for drill-down items. |
| `match` | Replaces `title` for Alfred's client-side filtering (when the object's `alfredfiltersresults` is true). |
| `type` | `"file"` makes the item act like a file (enables file actions; checks existence — `"file:skipcheck"` to skip). |
| `icon.path` | Relative to the workflow folder. `{"type":"fileicon","path":"/Applications/Safari.app"}` = that file's icon; `{"type":"filetype","path":"public.png"}` = UTI icon. |
| `mods` | Keys: `cmd`, `alt`, `ctrl`, `shift`, `fn` and `+`-combos. Each may override `subtitle`, `arg`, `valid`, `icon`, `variables`. Mod-level `variables` REPLACE item-level ones entirely — repeat what you still need. |
| `variables` | Set only when this item is actioned. |

## Minimal emitters

zsh (`type` 11, `scriptargtype` 1):

```sh
query="$1"
printf '{"items":[{"title":"Echo %s","arg":"%s"}]}' "$query" "$query"
```

For anything beyond trivial echoes, build the JSON with a real serializer — string
interpolation breaks on quotes in user input:

JXA (`type` 7):

```javascript
function run(argv) {
  const items = [{title: `Echo ${argv[0] ?? ""}`, arg: argv[0] ?? ""}];
  return JSON.stringify({items});
}
```

python3 via shim (`type` 0, inline script `/usr/bin/env python3 filter.py "$1"`):

```python
import json, sys
print(json.dumps({"items": [{"title": f"Echo {sys.argv[1]}"}]}))
```

## Empty results

Return `{"items": [{"title": "Nothing found", "valid": false}]}` rather than an empty
array — an empty `items` shows Alfred's fallback searches, which reads as a bug.
