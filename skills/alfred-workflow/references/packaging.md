# Packaging, Installing, Debugging, Distributing

## Workflow folder anatomy

```
my-workflow/
├── info.plist        # the workflow
├── icon.png          # workflow icon, ≥256×256 (optional but bare workflows look unfinished)
├── <object-uid>.png  # per-object canvas icons (optional)
├── scripts/          # external script files (chmod +x)
└── prefs.plist       # user's configured values — NEVER ship or commit this
```

All paths inside the workflow are relative to this folder. Keep dev helpers (plist
generators, test scripts) OUTSIDE the folder — everything in it ships in the package.

## Icon

A workflow without `icon.png` shows a generic gear everywhere Alfred displays it —
finish a workflow by giving it one. If no icon exists yet, generate it with an
available image-generation skill (e.g. `generate-image`):

- Ask for a **1024×1024 square PNG**, save as `icon.png` at the workflow root.
  Alfred scales it down; Gallery requires ≥256×256.
- Prompt for a **flat macOS-style app icon: one bold glyph, minimal detail,
  transparent background** — it must stay readable at ~32 px in Alfred's result list,
  so no text, no fine lines, no scenes.
- Verify/normalize with `sips --getProperty pixelWidth icon.png`; downscale if needed
  via `sips -z 512 512 icon.png`.

Per-object icons work the same way, saved as `<object-uid>.png`.

## Pack

`{{SKILL_DIR}}/scripts/pack.sh <dir> [out.alfredworkflow]` zips the folder *contents*
(info.plist at the archive root — zipping the parent folder breaks import) and
excludes `prefs.plist` and dotfiles.

Export behavior to remember: hotkey bindings and the category are stripped, snippet
trigger keywords are stripped on import, `variablesdontexport` values are blanked.
Document in the readme that users must bind their own hotkeys.

## Install on this machine

Two routes:

1. **Import dialog** (user-visible): `open My.alfredworkflow` — Alfred pops a
   confirmation window.
2. **Direct install** (silent, what dev loops use): copy the folder into Alfred's
   workflows directory under a `user.workflow.<UUID>` name, then tell Alfred to
   reload.

```bash
PREFS=$(python3 -c 'import json,os;print(json.load(open(os.path.expanduser("~/Library/Application Support/Alfred/prefs.json")))["current"])')
DEST="$PREFS/workflows/user.workflow.$(uuidgen)"
cp -R my-workflow "$DEST"
rm -f "$DEST/prefs.plist"
osascript -e 'tell application id "com.runningwithcrayons.Alfred" to reload workflow "com.user.myworkflow"'
```

The preferences dir is found via `prefs.json` because it is often relocated (iCloud /
Dropbox sync). Before overwriting an existing install, check whether a folder with the
same `bundleid` already exists and replace that folder instead of adding a duplicate —
two installed copies of one bundleid confuse Alfred.

Alfred indexes freshly copied folders with a few seconds' lag: `reload workflow` may
error with "not found" right after the copy even though `run trigger` already works.
Treat a failed reload as best-effort and retry once after a short wait.

## Smoke test without the GUI

- External trigger: `osascript -e 'tell application id "com.runningwithcrayons.Alfred" to run trigger "id" in workflow "bundle.id" with argument "x"'`
- Open Alfred with a query primed: `osascript -e 'tell application id "com.runningwithcrayons.Alfred" to search "keyword "'`

Then have the user open the workflow canvas: Alfred Preferences → Workflows. The
debugger (bug icon, top right of the canvas) shows each object's input/output and your
script's stderr.

## Distribution conventions (repo + Gallery)

- Repo layout: `info.plist` + `icon.png` at repo root, code in `scripts/`. Mark
  `info.plist` as `linguist-generated` in `.gitattributes` to mute diff noise.
- Don't commit built `.alfredworkflow` files; attach them to releases. Version bumps:
  `plutil -replace version -string "1.1" info.plist`.
- Gallery (alfred.app) requirements: fully self-contained (no runtime pip/brew/binary
  downloads), macOS-stock interpreters preferred, compiled binaries must be universal
  (arm64+x86_64) and signed+notarized, readme starts with `## Usage` and uses `<kbd>`
  tags, settings via User Configuration only.
- Bundled prebuilt binaries hit Gatekeeper quarantine — prefer scripts, or document
  `xattr -d com.apple.quarantine`.
