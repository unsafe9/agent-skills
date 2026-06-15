---
name: handoff
description: "Transfer a self-contained task to a separate, persistent agent surface that keeps working on its own — Codex app (via a `codex://` deeplink), Claude Code in tmux, or Codex CLI in tmux. Composes a self-contained brief, launches the surface, and reports where it is running; control moves to that surface and the work continues independently in its own app or terminal window. The point is to set up the work to live on elsewhere, not to wait on it here. Use when the user wants to continue work in another app or terminal, open or launch a task in Codex, spin up an autonomous background or tmux agent, or says 'handoff', 'continue this in tmux', 'open it in the Codex app', 'run it in the background'. When the user says codex, default to Codex app; use Codex CLI only when explicitly named."
---

# Handoff

Route a self-contained task to another agent surface.

## Choose Target

- **Codex app**: default when the user says `codex`, `Codex app`, `Codex Desktop`, `deeplink`, `open in Codex`, or wants to continue interactively in the app.
- **Claude Code in tmux**: use when the user says `tmux`, `background`, `autonomous`, `Claude Code`, or wants another terminal agent to keep working.
- **Codex CLI in tmux**: use only when the user explicitly says `codex-cli`, `Codex CLI`, or asks for the CLI rather than the app.

If the request is ambiguous and includes `codex`, choose Codex app.

## Compose Prompt

The receiving agent starts with zero conversation context. Make the handoff prompt self-contained:

- Task, goal, and success criteria
- Relevant file paths, repo paths, URLs, and constraints
- Expected output format
- Any current findings that matter

For tmux targets, append: `When the task is complete, ask if the user wants to close this tmux window. If yes: tmux kill-window`

## Codex App

Codex app handoff uses the `codex://` URL scheme. Official reference: https://developers.openai.com/codex/app/commands#deep-links

The `codex-app-handoff.sh` script builds and opens the deep link for you — a new thread by default, an existing one with `--thread-id`, or a workspace matched by Git remote with `--origin-url` (run it with `--help` for all options). Opening a deep link does not submit the prompt automatically; it prepares the app thread so the user can review and send it.

For short prompts, pass the prompt directly:

```bash
{{SKILL_DIR}}/scripts/codex-app-handoff.sh \
  --dir <absolute-workspace-dir> \
  --prompt <text>
```

For long prompts, write the handoff brief to a file and pass the file path:

```bash
{{SKILL_DIR}}/scripts/codex-app-handoff.sh \
  --dir <absolute-workspace-dir> \
  --prompt-file <handoff-brief.md>
```

Use `--print-only` to inspect the generated deep link without opening the app.

## tmux Targets

Use tmux when the user wants autonomous background work in a terminal session.

| Parameter | How to determine | Default |
|---|---|---|
| Session | Explicit `-s`/`--session`, or infer from task domain | `work` |
| Window | Short kebab-case task name, 3-5 words | required |
| Directory | Project path if the task targets a repo | current working directory |
| Prompt | Complete task for the receiving agent | required |

The tmux script creates the session if missing, otherwise creates a new window in the session. It prints `<session>:<window>` after launch. Use `--dry-run` to verify the resolved target and command without creating a tmux window.

### Claude Code

```bash
{{SKILL_DIR}}/scripts/tmux-handoff.sh \
  --agent claude \
  --session <session> \
  --window <window_name> \
  --prompt <text> \
  [--dir <path>] \
  [--claude-args '<extra flags>']
```

For long prompts, write a prompt file and use `--prompt-file <path>`. The script passes it to Claude Code as `@<path>`.

### Codex CLI

```bash
{{SKILL_DIR}}/scripts/tmux-handoff.sh \
  --agent codex \
  --session <session> \
  --window <window_name> \
  --prompt <text> \
  [--dir <path>] \
  [--codex-args '<extra flags>']
```

For long prompts, write a prompt file and use `--prompt-file <path>`. The script passes the file content as the initial Codex prompt.

## Report

After launching, report one concise line with the target and location:

- Codex app: `Opened the handoff in the Codex app.`
- tmux: `Launched the task in tmux. (<session> -> <window>)`
