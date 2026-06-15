# rescue

Run an external AI model on your task and bring its answer back into this
conversation — Claude Code (`claude`), Codex (`codex`), or Gemini/Antigravity
(`agy`) — for a second opinion, deeper investigation, implementation rescue, or a
large handoff; or run all three in parallel and synthesize a consensus.

## How it works

One of the three backends matches the host the skill runs under (the **host
backend**) and reasons natively through a subagent — no CLI subprocess. The other
two are reached through their command-line tools. So you only strictly need the
CLIs for the backends that are *not* your current host, but installing all three
unlocks single-backend rescue to any of them and the full 3-way consensus.

## Prerequisites

- **Host facility**: a runtime that can spawn subagents / delegate tasks (this is
  how the skill reaches both the native host backend and the CLI forwarders). The
  skill never shells out to a CLI directly — it always goes through a subagent.
- **External CLIs** (install + authenticate the ones you want as backends):
  - `claude` — [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code).
  - `codex` — Codex CLI (`codex exec`).
  - `agy` — Antigravity CLI (drives Gemini).
- **Services / auth**: each CLI manages its own login/credentials — make sure the
  ones you intend to use are signed in before invoking the skill.

A missing CLI is handled gracefully: single-backend rescue to an unavailable
backend reports that and stops, and consensus proceeds with whichever backends are
available, noting the one it skipped.

## Usage

Invoke with an optional backend and flags, then the task:

```
[claude|codex|gemini|consensus] [--background|--wait]
[--resume|--fresh|--conversation <id>] [--persist] [--model <model>]
[--effort <level>] [--add-dir <path>] [what to investigate, solve, or continue]
```

Naming exactly one backend routes to it; anything else — including a bare
`rescue` — runs the 3-way consensus.

A fresh single-backend run is **ephemeral by default**: where a CLI supports it,
the session is not persisted to disk, so a one-off rescue leaves nothing to resume.
Pass `--persist` to keep a fresh session resumable; `--resume` / `--conversation`
continue an existing saved session. (`agy` always persists, so `--persist` is a
no-op there.)

See `SKILL.md` for routing, session policy, and the consensus synthesis, and
`references/` for each backend's CLI invocation.
