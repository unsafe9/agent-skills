# User Configuration and Variables

## Variable scopes — pick the right one

| Scope | Where it lives | Use for |
|---|---|---|
| User Configuration | `userconfigurationconfig` in info.plist (defaults) + user values in `prefs.plist` | Anything the user should set: keywords, API keys, paths, options. Values never export with the workflow file. |
| Workflow variables | top-level `variables` dict | Internal constants (endpoint URLs). Exported — never secrets. List names in `variablesdontexport` to strip values on export. |
| Stream variables | set at runtime by Arg and Vars / JSON utility / Script Filter `variables` | Per-run state flowing through the graph. |

All variables reach scripts as environment variables and reach object text fields as
`{var:name}`. Inline transforms: `{var:name.uppercase}`, `.lowercase`, `.trim`,
`.reverse`, `.stripdiacritics` — they chain left-to-right
(`{var:name.trim.uppercase}` verified working). Other placeholders: `{query}`, `{clipboard}`,
`{clipboard:2}`, `{date}`, `{time}`, `{const:alfred_workflow_data}`,
`{const:alfred_workflow_cache}`.

## What to externalize — and how to use it

The scopes table says *where* each kind of value lives; this is *which* values to pull
out and how to wire them so the workflow is shareable and editable without opening the
canvas.

**The test:** would a user — or a second machine — reasonably want this different? If
so it is a User Configuration field, not a hardcoded value. In practice that means
**keywords/hotkeys, API keys & tokens, account or repo IDs, file/folder paths, target
app bundle IDs, model names, limits & counts, on/off toggles, and format choices.**
Keep hardcoded only what is genuinely fixed: the workflow's own logic, stable provider
endpoints (those can be top-level `variables`), and constants the user has no reason to
touch.

**Secrets are not negotiable.** API keys, tokens, passwords → a `required` `textfield`
in `userconfigurationconfig`, never a top-level `variable` and never inline in a
script. Top-level `variables` ship inside the exported `.alfredworkflow`, so a secret
there leaks to everyone you share with; User Configuration values stay in the user's
local `prefs.plist` and never export.

**Reference, don't duplicate.** In object fields write `{var:name}` (a Keyword's
`keyword` = `{var:keyword}` lets the user rebind without touching the graph). In
scripts read the same name straight from the environment (`$api_key`,
`os.environ["api_key"]`) — Alfred injects every configuration/workflow/stream variable
as an env var, so never parse `prefs.plist` yourself.

**Ship defaults so it runs out of the box.** Give every non-secret field a sensible
`default` (and a `placeholder` showing the expected shape); mark `required` only for the
few values that truly block the workflow — usually just the API key. A new user should
be usable after filling at most one field.

**Name variables for meaning, not the widget** (`max_results`, not `slider1`) — that
name is exactly what scripts read and what `{var:...}` resolves. Persist user data and
caches under `{const:alfred_workflow_data}` / `{const:alfred_workflow_cache}` (and the
matching env vars in scripts), never in the workflow folder — Alfred replaces that
folder on update.

## userconfigurationconfig

Array of dicts; each shows one field in the workflow's "Configure Workflow…" sheet.
Outer keys are always: `type`, `variable`, `label`, `description`, `config`.

```xml
<dict>
    <key>config</key>
    <dict>
        <key>default</key><string>kw</string>
        <key>placeholder</key><string></string>
        <key>required</key><false/>
        <key>trim</key><true/>
    </dict>
    <key>description</key><string>Keyword that triggers the search</string>
    <key>label</key><string>Search Keyword</string>
    <key>type</key><string>textfield</string>
    <key>variable</key><string>keyword</string>
</dict>
```

Per-type `config` keys (all verified against real workflows):

| type | config keys | Quirks |
|---|---|---|
| `textfield` | `default`, `placeholder`, `required`, `trim` | |
| `textarea` | `default`, `required`, `trim`, `verticalsize` (rows, 3 or 6) | |
| `checkbox` | `default` (bool), `required`, `text` | The label next to the box is `text` — NOT `label`. Scripts receive `"0"`/`"1"`. |
| `popupbutton` | `default`, `pairs` | `pairs` is an array of `[label, value]` 2-element arrays; `default` must equal one of the values. |
| `slider` | `defaultvalue`, `minvalue`, `maxvalue`, `markercount`, `onlystoponmarkers`, `showmarkers` | Numeric keys, not `default`. Scripts receive a numeric string. |
| `filepicker` | `default`, `filtermode`, `placeholder`, `required` | `filtermode`: 0 files, 1 folders. |

Every value arrives in scripts as a string — convert types yourself. `required` fields
block the workflow until the user fills them (good for API keys).

Always include the `userconfigurationconfig` key, even as an empty `<array/>` —
modern Alfred 5 workflows carry it.

## Runtime environment variables (auto-injected into every script)

| Variable | Meaning |
|---|---|
| `alfred_workflow_data` | Persistent data dir (create it yourself; not exported) |
| `alfred_workflow_cache` | Volatile cache dir (create it yourself; not exported) |
| `alfred_workflow_bundleid` / `_name` / `_version` / `_uid` | Workflow identity |
| `alfred_workflow_keyword` | Keyword that fired the current Script Filter |
| `alfred_preferences` | Path to `Alfred.alfredpreferences` |
| `alfred_version` / `alfred_version_build` | Alfred version |
| `alfred_debug` | `"1"` only while the debugger is open — gate verbose stderr logs on it |

## Controlling the stream from any script

Any Run Script can print this to stdout to set the downstream argument and variables —
and even reconfigure the next object's fields:

```json
{"alfredworkflow": {"arg": "next-arg", "variables": {"k": "v"},
                    "config": {"title": "overridden"}}}
```

`config` keys here override the connected object's config for this run only. The JSON
utility object (`utility.json`) is the no-script version of the same mechanism.
