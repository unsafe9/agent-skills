# handoff

Transfer a self-contained task to a separate, persistent agent surface that keeps
working on its own — the **Codex app** (via a `codex://` deeplink), **Claude Code in
tmux**, or **Codex CLI in tmux**. The skill composes a self-contained brief, launches
the surface, and reports where it is running; the work then continues independently
in its own app or terminal window.

## Prerequisites

- **Programs**:
  - `bash` and `python3` — the `codex://` deep link is built by `python3` inside
    `scripts/codex-app-handoff.sh`.
  - `tmux` — required for the two tmux targets.
  - A URL opener: macOS `open` or Linux `xdg-open` — used to open the Codex deep link.
- **Target surfaces** (set up the ones you intend to hand off to):
  - **Codex app** — the desktop app that registers the `codex://` URL scheme.
    Opening the deep link prepares a thread; it does not auto-submit the prompt.
    See the [Codex deep-link docs](https://developers.openai.com/codex/app/commands#deep-links).
  - **`claude`** — the Claude Code CLI, for the "Claude Code in tmux" target.
  - **`codex`** — the Codex CLI, for the "Codex CLI in tmux" target.
- **Services / auth**: each target surface manages its own login/credentials — sign in
  to the app or CLI you plan to use before handing off.

## Usage

Pick a target and launch it with the bundled scripts:

```bash
# Codex app (deep link)
scripts/codex-app-handoff.sh --dir <absolute-workspace-dir> --prompt <text>
scripts/codex-app-handoff.sh --dir <dir> --prompt-file <brief.md>   # long briefs
scripts/codex-app-handoff.sh ... --print-only                        # inspect link only

# Claude Code in tmux
scripts/tmux-handoff.sh --agent claude --session <s> --window <w> --prompt <text> [--dir <path>]

# Codex CLI in tmux
scripts/tmux-handoff.sh --agent codex --session <s> --window <w> --prompt <text> [--dir <path>]
```

Both scripts take `--prompt-file <path>` for long briefs and a no-op preview mode
(`--print-only` for the Codex app, `--dry-run` for tmux). Run either with `--help`
for the full option list. See `SKILL.md` for how to choose a target and compose the
handoff brief.
