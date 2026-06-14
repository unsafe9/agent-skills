# info.plist Object Reference

Every shape below was verified against real workflows (alfredapp official org,
1Password, gharlan/alfred-github-workflow) or Alfred 5's own files. Object `version`
integers are per-object schema versions Alfred writes — copy them as shown, they are
not the workflow version.

## Table of contents

1. [Object type index](#object-type-index)
2. [Top-level keys](#top-level-keys)
3. [Object envelope](#object-envelope)
4. [Connections](#connections)
5. [Script execution config](#script-execution-config)
6. [Triggers](#triggers)
7. [Inputs](#inputs)
8. [Actions](#actions)
9. [Utilities](#utilities)
10. [Outputs](#outputs)
11. [Automations](#automations)
12. [Invoking external triggers from outside Alfred](#invoking-external-triggers-from-outside-alfred)

Specialized objects' full schemas live in `objects-catalog.md` (read on demand) — this
file keeps the always-needed mechanics and the common-object schemas.

## Object type index

Every workflow object Alfred 5 exposes, with its exact `type` string. The string is
the one thing you can neither derive from code nor safely guess — a wrong one (e.g.
`action.filebuffer` instead of `action.buffer`, or `utility.fileconditional` instead
of `utility.file`) yields an object Alfred silently drops. Look the object up here
before placing it. The sections below carry full `config` shapes for the common
objects; the specialized ones — every User Interface view, the Automations extras, and
the long-tail triggers/inputs/actions/utilities/outputs — are detailed in
`objects-catalog.md`. *Category* is the GUI palette group the user sees — note a few
Automations-palette objects keep an `action.*` type for historical reasons.

Verified against Alfred 5.7.3. `version` is the per-object schema version Alfred
writes; it is 1 unless listed otherwise — copy the value shown, don't invent a higher
one. Strings below omit the shared `alfred.workflow.` prefix.

| Object | `type` | ver | Category |
|---|---|---|---|
| Hotkey | `trigger.hotkey` | 2 | Triggers |
| Remote | `trigger.remote` | 1 | Triggers |
| Snippet | `trigger.snippet` | 1 | Triggers |
| External | `trigger.external` | 1 | Triggers |
| File Action | `trigger.action` | 1 | Triggers |
| Universal Action | `trigger.universalaction` | 1 | Triggers |
| Contact Action | `trigger.contact` | 1 | Triggers |
| Fallback Search | `trigger.fallback` | 1 | Triggers |
| Keyword | `input.keyword` | 1 | Inputs |
| File Filter | `input.filefilter` | 2 | Inputs |
| Running Apps Filter | `input.runningappsfilter` | 1 | Inputs |
| Dictionary Lookup | `input.dictionaryfilter` | 1 | Inputs |
| List Filter | `input.listfilter` | 1 | Inputs |
| Script Filter | `input.scriptfilter` | 3 | Inputs |
| Open File | `action.openfile` | 3 | Actions |
| Launch Apps / Files | `action.launchfiles` | 1 | Actions |
| Reveal File in Finder | `action.revealfile` | 1 | Actions |
| Browse in Terminal | `action.browseinterminal` | 1 | Actions |
| Browse in Alfred | `action.browseinalfred` | 1 | Actions |
| Action in Alfred | `action.actioninalfred` | 1 | Actions |
| File Buffer | `action.buffer` | 1 | Actions |
| Default Web Search | `action.systemwebsearch` | 1 | Actions |
| Open URL | `action.openurl` | 1 | Actions |
| Run Script | `action.script` | 2 | Actions |
| Run NSAppleScript | `action.applescript` | 1 | Actions |
| Terminal Command | `action.terminalcommand` | 1 | Actions |
| Automation Task | `automation.task` | 1 | Automations |
| Run Shortcut | `automation.runshortcut` | 1 | Automations |
| System Command | `action.systemcommand` | 2 | Automations |
| Music Command | `action.itunescommand` | 1 | Automations |
| Grid View | `userinterface.grid` | 1 | User Interface |
| Image View | `userinterface.image` | 1 | User Interface |
| Text View | `userinterface.text` | 1 | User Interface |
| PDF View | `userinterface.pdf` | 1 | User Interface |
| Arg and Vars | `utility.argument` | 1 | Utilities |
| Split Arg | `utility.split` | 1 | Utilities |
| Join Args | `utility.joinargs` | 1 | Utilities |
| Junction | `utility.junction` | 1 | Utilities |
| Conditional | `utility.conditional` | 1 | Utilities |
| Dialog Conditional | `utility.dialog` | 1 | Utilities |
| File Conditional | `utility.file` | 1 | Utilities |
| Filter | `utility.filter` | 1 | Utilities |
| Delay | `utility.delay` | 1 | Utilities |
| Transform | `utility.transform` | 1 | Utilities |
| Replace | `utility.replace` | 2 | Utilities |
| Expression | `utility.expression` | 1 | Utilities |
| Random | `utility.random` | 1 | Utilities |
| Hide Alfred | `utility.hidealfred` | 1 | Utilities |
| Show Alfred | `utility.showalfred` | 1 | Utilities |
| JSON Config | `utility.json` | 1 | Utilities |
| Debug | `utility.debug` | 1 | Utilities |
| Post Notification | `output.notification` | 1 | Outputs |
| Large Type | `output.largetype` | 3 | Outputs |
| Copy to Clipboard | `output.clipboard` | 3 | Outputs |
| Write Text File | `output.writefile` | 1 | Outputs |
| Play Sound | `output.playsound` | 1 | Outputs |
| Speak | `output.speak` | 1 | Outputs |
| Dispatch Key Combo | `output.dispatchkeycombo` | 1 | Outputs |
| Call External Trigger | `output.callexternaltrigger` | 1 | Outputs |

## Top-level keys

| Key | Type | Required | Notes |
|---|---|---|---|
| `bundleid` | string | yes | Reverse-DNS, e.g. `com.user.myworkflow`. Identity for updates and data dirs. |
| `name` | string | yes | Display name. |
| `description` | string | yes | One-liner shown in the workflow list (may be empty). |
| `createdby` | string | yes | Author (may be empty). |
| `objects` | array | yes | The nodes. Order is irrelevant — the graph comes from `connections`. |
| `connections` | dict | yes | source uid → array of connection dicts. |
| `uidata` | dict | yes | uid → canvas position. See `layout.md`. |
| `disabled` | bool | yes | `false` for new workflows. |
| `userconfigurationconfig` | array | Alfred 5 | Include even when empty (`<array/>`). See `config-and-variables.md`. |
| `readme` | string | no | Markdown shown in the README tab. |
| `version` | string | no | Workflow version, free-form (`"1.0"`, `"2026.1"`). |
| `category` | string | no | Stripped on export; harmless to set. |
| `webaddress` | string | no | "Visit website" URL. |
| `variables` | dict | no | Workflow-level defaults. Exported with the file — no secrets. |
| `variablesdontexport` | array | no | Variable names excluded from export. |

## Object envelope

```xml
<dict>
    <key>config</key><dict><!-- per-type keys --></dict>
    <key>type</key><string>alfred.workflow.CATEGORY.NAME</string>
    <key>uid</key><string>1A2B3C4D-0000-4000-8000-1234567890AB</string>
    <key>version</key><integer>1</integer>
</dict>
```

- `uid`: UPPERCASE UUID, unique per object. `uuidgen` produces the right format.
- `config` is absent only for `utility.junction`.
- Terminal nodes (outputs) either have no `connections` entry or an empty `<array/>`.

## Connections

```xml
<key>connections</key>
<dict>
    <key>SOURCE-UID</key>
    <array>
        <dict>
            <key>destinationuid</key><string>DEST-UID</string>
            <key>modifiers</key><integer>0</integer>
            <key>modifiersubtext</key><string></string>
            <key>vitoclose</key><false/>
            <!-- only on conditional branch edges: -->
            <key>sourceoutputuid</key><string>CONDITION-UID</string>
        </dict>
    </array>
</dict>
```

- `modifiers` bitmask (combinable by addition): `0` none, `131072` ⇧shift,
  `262144` ⌃ctrl, `524288` ⌥opt, `1048576` ⌘cmd. A nonzero value makes this edge an
  alternative action that fires only while that key is held; put a human label in
  `modifiersubtext` (it shows in Alfred's result subtitle).
- Modifier edges vs Script Filter JSON `mods`: use a modifier **edge** when the key
  should route to a *different downstream object*; use item-level `mods` in the
  Script Filter JSON when the key keeps the same route but changes the *argument or
  subtitle* (see `script-filter-json.md`). Don't build both for the same key.
- `vitoclose` (sic — Alfred's historical typo): the window-behavior flag for this
  edge (the GUI's square "window stays open" marker on a connection). Virtually every
  real edge carries `false` and Alfred closes normally when a result is actioned —
  leave it `false` unless replicating behavior you verified in the GUI.
- `sourceoutputuid` appears only on edges leaving a Conditional through a named
  condition output; its value is that condition's `uid` (see Conditional below). The
  edge without `sourceoutputuid` is the else branch.

## Script execution config

Used inside `input.scriptfilter` and `action.script`:

| Key | Meaning |
|---|---|
| `type` | Interpreter integer. Verified: `0` `/bin/bash`, `2` `/usr/bin/ruby`, `7` JXA (`osascript -l JavaScript`), `8` External Script (runs `scriptfile`), `11` `/bin/zsh`. `1` was PHP (gone from macOS — avoid). Other integers are unverified. |
| `scriptargtype` | `1` = input arrives as argv (`$1`) — use this. `0` = literal `{query}` substitution in the script text, needs `escaping`. |
| `script` | Inline script text. XML-escape via a plist library, never by hand. |
| `scriptfile` | Path relative to the workflow folder. **Requires `type` = 8** — with any other `type` Alfred runs the inline `script` instead, and an emptied inline shows up as silently empty results. The file must be executable; its shebang picks the interpreter. |
| `escaping` | Bitmask for `{query}` mode. `102` is the value modern workflows carry; irrelevant when `scriptargtype` = 1 but keep it. |
| `concurrently` | (`action.script` only) `true` = allow parallel instances. |

Both `script` and `scriptfile` keys must be present; the unused one is `<string></string>`.
Inline scripts get the interpreter from `type` — no shebang needed. Keep inline scripts
to a few lines; anything longer goes in `scripts/` inside the workflow folder, run one
of two verified ways: `scriptfile` + `type` 8, or a one-line inline shim such as
`/usr/bin/python3 scripts/foo.py "$1"` under `type` 0/11 (the official 1Password
workflow's pattern).

## Triggers

### External Trigger — `alfred.workflow.trigger.external` (version 1)

```xml
<key>config</key>
<dict>
    <key>availableviaurlhandler</key><false/>
    <key>triggerid</key><string>my_trigger</string>
</dict>
```

### Hotkey — `alfred.workflow.trigger.hotkey` (version 2)

Ship it unbound (`hotkey`/`hotmod` = 0): bindings are stripped on export anyway and the
user assigns their own.

```xml
<key>config</key>
<dict>
    <key>action</key><integer>0</integer>
    <key>argument</key><integer>0</integer>
    <key>focusedappvariable</key><false/>
    <key>focusedappvariablename</key><string></string>
    <key>hotkey</key><integer>0</integer>
    <key>hotmod</key><integer>0</integer>
    <key>leftcursor</key><false/>
    <key>modsmode</key><integer>0</integer>
    <key>relatedAppsMode</key><integer>0</integer>
</dict>
```

`argument`: 0 none, 1 selection in macOS, 2 clipboard contents, 3 static text (then add
`argumenttext`).

### Universal Action — `alfred.workflow.trigger.universalaction` (version 1)

```xml
<key>config</key>
<dict>
    <key>acceptsfiles</key><false/>
    <key>acceptsmulti</key><integer>0</integer>
    <key>acceptstext</key><true/>
    <key>acceptsurls</key><false/>
    <key>name</key><string>Shown in the Universal Actions panel</string>
</dict>
```

### Others

File Action, Remote, Snippet, Fallback Search, Contact Action → `objects-catalog.md`.

## Inputs

### Keyword — `alfred.workflow.input.keyword` (version 1)

```xml
<key>config</key>
<dict>
    <key>argumenttype</key><integer>1</integer>
    <key>keyword</key><string>{var:my_keyword}</string>
    <key>subtext</key><string>Shown under the title</string>
    <key>text</key><string>Result row title</string>
    <key>withspace</key><true/>
</dict>
```

`argumenttype` (also on Script Filter and List Filter): `0` argument required,
`1` optional, `2` none — verified against installed workflows. Make keywords
user-configurable with `{var:...}`.

### Script Filter — `alfred.workflow.input.scriptfilter` (version 3)

Full modern shape (JXA example; for zsh set `type` 11):

```xml
<key>config</key>
<dict>
    <key>alfredfiltersresults</key><false/>
    <key>alfredfiltersresultsmatchmode</key><integer>0</integer>
    <key>argumenttreatemptyqueryasnil</key><true/>
    <key>argumenttrimmode</key><integer>0</integer>
    <key>argumenttype</key><integer>1</integer>
    <key>escaping</key><integer>102</integer>
    <key>keyword</key><string>{var:keyword}</string>
    <key>queuedelaycustom</key><integer>3</integer>
    <key>queuedelayimmediatelyinitially</key><true/>
    <key>queuedelaymode</key><integer>0</integer>
    <key>queuemode</key><integer>1</integer>
    <key>runningsubtext</key><string>Loading…</string>
    <key>script</key><string>// see script-filter-json.md</string>
    <key>scriptargtype</key><integer>1</integer>
    <key>scriptfile</key><string></string>
    <key>skipuniversalaction</key><true/>
    <key>subtext</key><string>Subtitle in Alfred's default results</string>
    <key>title</key><string>Title in Alfred's default results</string>
    <key>type</key><integer>7</integer>
    <key>withspace</key><false/>
</dict>
```

- `alfredfiltersresults` `true` = run script once, let Alfred filter items client-side
  (`matchmode` 0 exact-from-start+word-boundary, 1 exact-from-start, 2 word-match any
  order, 3 word-match sequential). `false` = script reruns per keystroke and does its
  own filtering.
- Run behaviour (the GUI's "Run Behaviour" sheet; mappings verified against a live
  GUI↔plist pair):
  - `queuemode` `1` = wait until the previous run finishes — the default everywhere,
    right for fast local scripts (results stay visible while typing). The GUI's
    "terminate previous script" alternative suits slow scripts whose stale runs
    waste time; its integer is unverified — flip it once in the GUI and copy the
    value if you need it.
  - `queuedelaymode` `0` = queue a run after every keystroke;
    `queuedelayimmediatelyinitially` `true` = fire instantly on the first typed
    character. `queuedelaycustom` merely stores the custom-delay choice and is
    present even when unused.
  - `argumenttrimmode` `0` = trim irrelevant trailing whitespace so trailing spaces
    don't trigger pointless re-runs. Keep 0.
  - Rule of thumb: fast local script → keep the defaults above (`1`/`0`/`true`/`0`);
    slow or rate-limited script (web API) → delay runs until typing pauses (set the
    delay in the GUI) and prefer Script Filter `cache` + `loosereload` over fighting
    the queue.
- `argumenttreatemptyqueryasnil` (the GUI's "Don't set argv when query is empty"
  checkbox): `true` = an empty query passes no argv at all (script sees `$1` unset).
  Set `false` when an empty query should still run the script with `""` — e.g. a
  launcher that lists everything before you type.
- Script output protocol: `references/script-filter-json.md`.

### List Filter — `alfred.workflow.input.listfilter` (version 1)

`items` is a **JSON string embedded in the plist**, not a plist array:

```xml
<key>config</key>
<dict>
    <key>argumenttrimmode</key><integer>0</integer>
    <key>argumenttype</key><integer>1</integer>
    <key>fixedorder</key><false/>
    <key>items</key>
    <string>[{"title":"First","subtitle":"Pick me","arg":"first"},{"title":"Second","arg":"second"}]</string>
    <key>keyword</key><string>{var:keyword}</string>
    <key>matchmode</key><integer>0</integer>
    <key>runningsubtext</key><string></string>
    <key>subtext</key><string></string>
    <key>title</key><string>My List</string>
    <key>withspace</key><true/>
</dict>
```

Omit `keyword` (and `withspace`) when the List Filter is reached mid-graph from
another object rather than typed directly — it is not an entry point then.

Avoid feeding a typed input INTO a List Filter (Keyword → List Filter): each hop
costs an Enter, and the passed argument lands in the List Filter's query box where
it filters the items — the list looks empty until the user clears the text. For
"apply one of N operations to typed text", use a single Script Filter that previews
each operation's result in the item subtitles instead
(`references/ux-and-performance.md`).

### Others

File Filter, Running Apps Filter, Dictionary Lookup → `objects-catalog.md`.

## Actions

### Run Script — `alfred.workflow.action.script` (version 2)

Input arrives as `$1` (argv mode). Full shape:

```xml
<key>config</key>
<dict>
    <key>concurrently</key><false/>
    <key>escaping</key><integer>102</integer>
    <key>script</key><string>./scripts/do_thing.sh "$1"</string>
    <key>scriptargtype</key><integer>1</integer>
    <key>scriptfile</key><string></string>
    <key>type</key><integer>11</integer>
</dict>
```

### Open URL — `alfred.workflow.action.openurl` (version 1)

```xml
<key>config</key>
<dict>
    <key>browser</key><string></string> <!-- empty = default browser -->
    <key>skipqueryencode</key><false/>  <!-- true = don't %-encode the query -->
    <key>skipvarencode</key><false/>    <!-- true = don't %-encode {var:...} -->
    <key>spaces</key><string></string>
    <key>url</key><string>https://example.com/search?q={query}</string>
</dict>
```

Alfred 5.7.3 replaced the old `utf8` key with `skipqueryencode`/`skipvarencode` — a
re-save drops `utf8`.

### Terminal Command — `alfred.workflow.action.terminalcommand` (version 1)

`script` (string — the command line; the key is `script`, **not** `command`),
`escaping` (102). Opens a visible Terminal — use Run Script when visibility is not
needed.

### Others

Specialized actions — Default Web Search, Action in Alfred, File Buffer, Open File,
Launch Apps / Files, Reveal in Finder, Browse in Terminal/Alfred, Run NSAppleScript →
`objects-catalog.md`. (System Command and Music Command sit in the Automations palette
section despite their `action.*` type strings.)

## Utilities

### Arg and Vars — `alfred.workflow.utility.argument` (version 1)

The workhorse for reshaping the stream:

```xml
<key>config</key>
<dict>
    <key>argument</key><string>{query}</string> <!-- new stream arg; placeholders OK -->
    <key>passthroughargument</key><false/>      <!-- true = keep arg untouched (preserves arrays/file lists) -->
    <key>variables</key>
    <dict>
        <key>mode</key><string>search</string>
    </dict>
</dict>
```

### Conditional — `alfred.workflow.utility.conditional` (version 1)

```xml
<key>config</key>
<dict>
    <key>conditions</key>
    <array>
        <dict>
            <key>inputstring</key><string>{var:mode}</string>
            <key>matchcasesensitive</key><false/>
            <key>matchmode</key><integer>0</integer>
            <key>matchstring</key><string>search</string>
            <key>outputlabel</key><string>Search mode</string>
            <key>uid</key><string>CONDITION-UUID-REFERENCED-BY-EDGES</string>
        </dict>
    </array>
    <key>elselabel</key><string>else</string>
    <key>hideelse</key><false/>
</dict>
```

`matchmode` observed in real workflows: `0` is equal to (with `matchstring`), `1` and
`5` appear with empty `matchstring` as "is not empty", `2` matches regex. The full
enum is not documented — when the routing semantics matter, prefer `0` (equality
against an explicit value, the unambiguous case) or `2` (regex), and verify other
modes by round-tripping one Conditional through the Alfred GUI. Each condition's
`uid` is what edges reference via `sourceoutputuid`.

### Split Arg — `alfred.workflow.utility.split` (version 1)

`delimiter`, `discardemptyarguments`, `trimarguments`, `outputas` (`0` variables /
`1` multiple args), `variableprefix`.

### Join Args — `alfred.workflow.utility.joinargs` (version 1)

Inverse of Split Arg — concatenates the incoming arguments into one string. Single key:

```xml
<key>config</key>
<dict>
    <key>delimiter</key><string>,</string>
</dict>
```

### JSON — `alfred.workflow.utility.json` (version 1)

Single key `json`: a raw JSON string in the `{"alfredworkflow": {"arg", "config",
"variables"}}` shape — can also reconfigure the *next* object via `config`. See
`config-and-variables.md`.

### Transform — `alfred.workflow.utility.transform` (version 1)

`type` int (`0` trim observed). Prefer inline `{var:name.uppercase}`-style transforms
in an Arg and Vars where possible.

### Junction — `alfred.workflow.utility.junction` (version 1)

No `config` key at all. Use to tidy many-to-one edges.

### Others

Filter, Delay, Debug, Replace, Expression, Random, Dialog Conditional, File Conditional
(`utility.file` — short name), Hide/Show Alfred → `objects-catalog.md`.

## Outputs

### Post Notification — `alfred.workflow.output.notification` (version 1)

```xml
<key>config</key>
<dict>
    <key>lastpathcomponent</key><false/>
    <key>onlyshowifquerypopulated</key><true/>
    <key>removeextension</key><false/>
    <key>text</key><string>{query}</string>
    <key>title</key><string>Done</string>
</dict>
```

`lastpathcomponent` `true` shows only the basename when `{query}` is a path
("Opened my-project", not the full path). `onlyshowifquerypopulated` `true`
suppresses the notification entirely when the input is empty — flip to `false` if
the notification must always appear.

### Copy to Clipboard — `alfred.workflow.output.clipboard` (version 3)

```xml
<key>config</key>
<dict>
    <key>autopaste</key><false/>
    <key>clipboardtext</key><string>{query}</string>
    <key>ignoredynamicplaceholders</key><false/>
    <key>transient</key><false/>
</dict>
```

### Large Type — `alfred.workflow.output.largetype` (version 3)

`largetypetext` (usually `{query}`), `alignment`, `font`, `textcolor`,
`backgroundcolor`, `fadespeed`, `fillmode`, `wrapat`, `ignoredynamicplaceholders`.

### Call External Trigger — `alfred.workflow.output.callexternaltrigger` (version 1)

```xml
<key>config</key>
<dict>
    <key>externaltriggerid</key><string>my_trigger</string>
    <key>passinputasargument</key><true/>
    <key>passvariables</key><true/>
    <key>workflowbundleid</key><string>self</string> <!-- or another workflow's bundleid -->
</dict>
```

The native way to loop or chain within/between workflows — faster than AppleScript.

### Others

Write Text File, Play Sound, Speak, Dispatch Key Combo → `objects-catalog.md`.

## Automations

The Automations palette section. Automation Task is detailed below; Run Shortcut
(`automation.runshortcut`), System Command, and Music Command are in `objects-catalog.md`.

### Automation Task — `alfred.workflow.automation.task` (version 1)

```xml
<key>config</key>
<dict>
    <key>tasksettings</key>
    <dict>
        <key>target_app</key><string>com.apple.Safari</string>
    </dict>
    <key>taskuid</key><string>com.alfredapp.automation.core/macOS/app.running</string>
</dict>
```

A task's input is the incoming stream argument (what `{query}` holds at that point);
`tasksettings` only sets the task's configured options. To feed a task a stored
variable, put an Arg and Vars with `argument` = `{var:name}` in front of it.

The full installed catalog is enumerable on disk:
`~/Library/Application Support/Alfred/Automation/Tasks/<group>/<category>/<task>/alfredtask.json`.
`taskuid` = `<group>/<category>/<task-dir-name>`; the descriptor's
`configurableConfig[].variable` names are exactly the keys allowed in `tasksettings`
(omit a key to accept its default). Read the descriptor before wiring a task — do not
guess setting names. `inputType`/`outputType` in the descriptor tell you what flows in
and out. Settings values accept placeholders, including
`{const:alfred_workflow_cache}` / `{const:alfred_workflow_data}` for Alfred's
directories.

## Invoking external triggers from outside Alfred

```bash
osascript -e 'tell application id "com.runningwithcrayons.Alfred" to run trigger "my_trigger" in workflow "com.user.myworkflow" with argument "hello"'
open "alfred://runtrigger/com.user.myworkflow/my_trigger/?argument=hello"
```

These are also how you smoke-test an installed workflow without touching the keyboard.
