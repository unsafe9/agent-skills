# info.plist Object Catalog — specialized objects

Detailed shapes for the objects you reach for occasionally. The type index in
`objects.md` lists every object and marks which ones live here; `objects.md` itself
carries the always-needed mechanics and the common-object schemas. Read this file
only when the index points you here.

The `config` key sets below are verified against an Alfred 5.7.3 canonical re-save:
Alfred drops keys it doesn't recognize and fills its own defaults on save, so these are
the keys it actually keeps. Copy `version` integers as shown. Enum/int values are
GUI-picked — when a specific value matters, set it once in the GUI and copy it back from
the re-saved plist.

## Table of contents

1. [User Interface](#user-interface)
2. [Triggers (specialized)](#triggers-specialized)
3. [Inputs (specialized)](#inputs-specialized)
4. [Actions (specialized)](#actions-specialized)
5. [Automations (specialized)](#automations-specialized)
6. [Utilities (specialized)](#utilities-specialized)
7. [Outputs (specialized)](#outputs-specialized)

## User Interface

View objects render their own window instead of returning rows to Alfred's result
list. Reach for one whenever the output can't be expressed as a Script Filter row +
subtitle — a rendered Markdown readout, an image grid, a PDF. Bending a Script Filter
or Large Type into a display surface is the usual mistake these objects exist to avoid.

### Text View — `alfred.workflow.userinterface.text` (version 1)

A scriptable, Markdown-capable pane — the object behind chat/readout UIs (e.g. the
official ChatGPT workflow's conversation view):

```xml
<key>config</key>
<dict>
    <key>behaviour</key><integer>2</integer>      <!-- how a rerun updates the view -->
    <key>fontmode</key><integer>0</integer>
    <key>fontsizing</key><integer>0</integer>
    <key>footertext</key><string>↩ Send · ⌘↩ New</string> <!-- key-hint line along the bottom -->
    <key>inputfile</key><string>chatgpt</string>  <!-- bundled file rendered as the body; empty = use the stream -->
    <key>inputtype</key><integer>1</integer>
    <key>loadingtext</key><string>Loading…</string>
    <key>outputmode</key><integer>1</integer>     <!-- 1 = render Markdown -->
    <key>scriptinput</key><integer>2</integer>
    <key>spellchecking</key><integer>0</integer>
    <key>stackview</key><false/>
</dict>
```

Perf: a script- or `rerun`-driven Text View re-runs its script on every update — keep
it cheap and cache expensive content (`ux-and-performance.md`).

### Grid View — `alfred.workflow.userinterface.grid` (version 1)

Filterable grid of image/file tiles (emoji pickers, GIF browsers):

```xml
<key>config</key>
<dict>
    <key>columncount</key><integer>4</integer>
    <key>filterable</key><true/>          <!-- type-to-filter the tiles -->
    <key>fixedorder</key><false/>
    <key>imageaspect</key><integer>0</integer>
    <key>inputfile</key><string></string> <!-- empty = tiles come from the stream -->
    <key>inputtype</key><integer>0</integer>
    <key>loadingtext</key><string></string>
    <key>showtitles</key><true/>
    <key>showsubtitles</key><true/>
    <key>titlesinfooter</key><false/>
    <key>subtitlesinfooter</key><false/>
</dict>
```

Perf: cache and parallel-fetch remote image tiles with placeholders while cold, like
item icons; never fetch them while the user filters (`ux-and-performance.md`).

### Image View — `alfred.workflow.userinterface.image` (version 1)

`imageresizemode` (int), `stackview` (bool). Shows one image, auto-sized.

### PDF View — `alfred.workflow.userinterface.pdf` (version 1)

`displaymode` (int), `stackview` (bool). Views and interacts with a PDF in-window.

`stackview` controls whether the view replaces Alfred's window or stacks on top of it;
when it should replace, the preceding object is often a Hide Alfred with
`config.unstackview` `true`. Copy that pairing from a real instance (e.g. the official
thumbnail-navigation workflow) rather than reconstructing it from scratch.

## Triggers (specialized)

- **File Action** `trigger.action`: `name` (label in the actions list), `acceptsmulti`
  (0/1 — accept multiple selected files).
- **Remote** `trigger.remote`: `argumenttype` (int), `workflowonly` (bool).
- **Snippet** `trigger.snippet`: `keyword` (e.g. `!probe`), `focusedappvariable` (bool),
  `focusedappvariablename` (string). Stripped on import — the user re-creates it.
- **Fallback Search** `trigger.fallback`: empty `config` (`<dict/>`); its title/subtext
  are set in Alfred's Features prefs, not here.
- **Contact Action** `trigger.contact`: `name` (label in the Contacts viewer).

## Inputs (specialized)

- **File Filter** `input.filefilter` (v2): `keyword`, `title`, `subtext`, `withspace`,
  `argumenttype`, `argumenttrimmode`, `scopes` (array of search-scope paths), `types`
  (array of UTIs), `fields` (array), `includesystem`/`anchorfields` (bool), `daterange`,
  `sortmode`, `limit` (ints), `runningsubtext`. Keep `scopes`/`types` narrow — see
  `ux-and-performance.md`.
- **Running Apps Filter** `input.runningappsfilter`: `keyword`, `title`, `subtext`,
  `withspace`, `argumenttype`, `outputprefix`, `outputtype` (int).
- **Dictionary Lookup** `input.dictionaryfilter`: `keyword`, `title`, `subtext`,
  `language` (empty = default), `showallwords` (bool).

## Actions (specialized)

### Default Web Search — `alfred.workflow.action.systemwebsearch` (version 1)

Fires one of Alfred's built-in web searches with the streamed argument:

```xml
<key>config</key>
<dict>
    <key>browser</key><string></string> <!-- empty = default browser -->
    <key>searcher</key><integer>1635215215</integer>
</dict>
```

`searcher` is the integer id of a built-in search (the example is Google) — not
guessable. Pick the search in the GUI once and copy its value.

### Action in Alfred — `alfred.workflow.action.actioninalfred` (version 1)

Shows Alfred's Universal Actions panel for the argument, optionally pre-selecting one
action so the user lands on it:

```xml
<key>config</key>
<dict>
    <key>jumpto</key><string>alfred.action.openwith</string> <!-- empty = no preselection -->
    <key>path</key><string>{query}</string>
    <key>type</key><integer>100</integer> <!-- kind of argument; 100 observed for a file path -->
</dict>
```

### File Buffer — `alfred.workflow.action.buffer` (version 1)

Manipulates Alfred's file buffer (the multi-item tray) and emits its contents:

```xml
<key>config</key>
<dict>
    <key>addfilestobuffer</key><false/>
    <key>clearbuffer</key><true/>
    <key>outputtype</key><integer>0</integer>
</dict>
```

### Others

- **Open File** `action.openfile` (v3): `sourcefile` (path / `{query}`), `openwith`
  (app path; empty = default app).
- **Launch Apps / Files** `action.launchfiles`: `paths` (array), `toggle` (bool —
  toggle app visibility).
- **Reveal in Finder** `action.revealfile`: `path` (string).
- **Browse in Terminal** `action.browseinterminal`: `path` (string).
- **Browse in Alfred** `action.browseinalfred`: `path`, `sortBy`/`sortDirection` (int),
  `sortFoldersAtTop`/`sortOverride`/`stackBrowserView` (bool).
- **Run NSAppleScript** `action.applescript`: `applescript` (the script, wrapped
  `on alfred_script(q) … end alfred_script`), `cachescript` (bool). Uses `applescript`,
  **not** the `script`/`scriptargtype` keys of a Run Script.

## Automations (specialized)

System Command and Music Command keep `action.*` type strings (see the index) but the
user finds them in the Automations palette section alongside Automation Task (detailed
in `objects.md`).

### Run Shortcut — `alfred.workflow.automation.runshortcut` (version 1)

Runs a macOS Shortcut directly — simpler than an Automation Task pointed at the
shortcuts category:

```xml
<key>config</key>
<dict>
    <key>inputmode</key><integer>-1</integer>
    <key>outputmode</key><integer>0</integer>
    <key>shortcut</key><string>My Shortcut Name</string>
</dict>
```

Perf: runs synchronously and pays the Shortcuts app's cold-start — keep it off live or
`rerun` paths; place it after the user acts (`ux-and-performance.md`).

### System Command — `alfred.workflow.action.systemcommand` (version 2)

`command` (int — which system action, GUI-picked), `confirm` (bool — show a
confirmation dialog first). Pick the action in the GUI and copy `command`.

### Music Command — `alfred.workflow.action.itunescommand` (version 1)

Single key `command` (int): controls Music.app — play/pause, next, volume, etc.
(`1` = play/pause observed). Pick the exact action in the GUI and copy the value.

## Utilities (specialized)

Watch the short type names: Dialog Conditional is `utility.dialog`, **File Conditional
is `utility.file`**.

- **Filter** `utility.filter` (legacy — prefer Conditional): `inputstring`, `matchmode`
  (int), `matchstring`, `matchcasesensitive` (bool). Stops the stream unless the test passes.
- **Delay** `utility.delay`: `seconds` (a **string** number, e.g. `"1"`). Pauses the stream.
- **Replace** `utility.replace` (**v2**): `matchmode` (int), `matchstring`, `replacestring`.
- **Expression** `utility.expression`: `expression` (string, e.g. `{query} * 2`). Maths on the stream.
- **Random** `utility.random`: `type` (int — UUID / number / list pick), `words`
  (newline-separated list when type = list), `wordseparatortype` (int).
- **Dialog Conditional** `utility.dialog`: `title`, `description`, `button1`/`button2`/
  `button3` (button labels; empty = unused). Routes on which button was pressed.
- **File Conditional** `utility.file`: `outputfileuti` (bool), `fileutivariablename`
  (string). Branches via its two connection outputs on whether the arg is an existing file.
- **Hide Alfred** `utility.hidealfred`: `unstackview` (bool).
- **Show Alfred** `utility.showalfred`: `argument` (string), `leftcursor` (bool).
- **Debug** `utility.debug`: `argument`, `cleardebuggertext`/`processoutputs` (bool).

## Outputs (specialized)

- **Write Text File** `output.writefile`: `filename`, `filetext`, `type` (int),
  `relativepathmode` (int), `createintermediatefolders`/`adduuid`/`allowemptyfiles`/
  `ignoredynamicplaceholders` (bool). (No `destination`/`mode` keys.)
- **Play Sound** `output.playsound`: `soundname` (string), `systemsound` (bool).
- **Speak** `output.speak`: `text` (string), `usevoiceover` (bool).
- **Dispatch Key Combo** `output.dispatchkeycombo`: `keycode` (int; `-1` = unset),
  `keymod` (int bitmask), `keychar` (string), `count` (int), `overridewithargument` (bool).
