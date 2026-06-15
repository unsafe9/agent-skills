---
name: rescue
description: "Run an external AI model on your task and bring its answer back into this conversation — Claude Code (`claude`), Codex (`codex`), or Gemini/Antigravity (`agy`) for a second opinion, a second model, deeper root-cause investigation, or substantial coding/diagnosis help, with the result returned here; or run all three in parallel and synthesize a consensus. The work happens elsewhere but the output comes back to you. Use whenever the current agent is stuck, wants an independent pass or a second model, needs deeper investigation, or wants another model to do a substantial coding or diagnosis task and report back. Triggers on 'rescue', 'second opinion', 'second model', a named backend (claude, claude-rescue, codex, codex-rescue, spark, gemini, gemini-rescue, agy, antigravity), or — for multiple perspectives — 'consensus', 'ask other agents', 'get multiple perspectives', 'what do others think', 'validate this approach', 'validate this decision'. Naming exactly one backend routes to it; anything else, including a bare 'rescue', runs the 3-way consensus."
argument-hint: [claude|codex|gemini|consensus] [--background|--wait] [--resume|--fresh|--conversation <id>] [--persist] [--model <model>] [--effort <level>] [--add-dir <path>] [what to investigate, solve, or continue]
---

# Rescue

Single entrypoint for delegating to one of three AI backends — Claude Code
(`claude`), Codex (`codex`), or Gemini/Antigravity (`agy`) — or running all three in
parallel for a synthesized consensus. The backend matching the current host runs
natively; the others run through their CLIs.

This skill owns routing, session policy, and consensus synthesis. The per-backend
reference files in `{{SKILL_DIR}}/references/` own the actual CLI invocation. The
skill itself never runs a CLI or solves the task, and there are no custom rescue
agents — it delegates through the available subagent/delegation facility.

### The host backend

One of the three backends matches the agent currently running this skill — the **host
backend** (`claude` on a Claude Code host, `codex` on a Codex host, `gemini` on a
Gemini/Antigravity host). A subagent is already a fresh, independent instance of the
host system, so for the host backend it reasons **natively** — no CLI subprocess. The
other two backends are reached only through their CLIs, per their reference files.
This keeps the skill host-neutral: whichever system you run under is the native
perspective, and the other two are the external ones.

### Context to carry

Every backend you spawn — native subagent or CLI forwarder — starts with none of this
conversation's context. It sees only the task text you forward plus whatever it reads
from the repo itself. So before forwarding, fold the parts that live only in this
conversation — findings so far, decisions made, ruled-out paths, constraints, and the
file or path pointers that matter — into the task text. This is not repo investigation
(the backend does that itself); it is transferring what this conversation already
knows. Consensus adds to this: it may also read referenced files and embed their
content, since each analyst evaluates a self-contained question.

Resolve `{{SKILL_DIR}}` to this skill's directory before pointing a subagent at a
reference file.

Raw user request:
$ARGUMENTS

If the host did not expand `$ARGUMENTS`, treat the user's current message as the
request rather than the literal string.

## Routing

Pick the mode from the request:

| Signal in the request | Mode |
|---|---|
| Names exactly one backend — `claude`/`claude-rescue`, `codex`/`codex-rescue`/`spark`, `gemini`/`gemini-rescue`/`agy`/`antigravity` | Single-backend rescue → that backend |
| `consensus`, multiple perspectives, ask other agents, what do others think, validate this approach/decision | Consensus (all three) |
| Anything else — a bare "rescue" / "second opinion" / "second model" with no backend named, or an ambiguous request | Consensus (all three) — the default |

Only an explicitly named single backend bypasses consensus. When in doubt, run
consensus.

If the user supplied no task at all, ask what to investigate, review, or fix
before routing.

## Consensus mode

Read `{{SKILL_DIR}}/references/consensus.md` and follow it. It covers stance
assignment, the parallel spawn of all three backends, the per-analyst prompt
template, and the synthesis structure.

## Single-backend rescue

### Session and execution policy

This policy is shared across all three backends; the reference translates the
resulting flags into the CLI invocation.

- `--background`: run the subagent in the background when the host supports
  background delegation. `--wait`: foreground. Neither: foreground.
- `--background` / `--wait` are host-level execution controls. Do not forward them
  into the CLI or the subagent's task text.
- For a background run, return only the host's background handle or status. Do not
  claim to have the final output yet.
- If the request already includes `--resume`, `--fresh`, or `--conversation <id>`,
  the user chose; do not ask about session.
- If no session flag is present and the request is clearly a follow-up to prior
  rescue work ("continue", "keep going", "resume", "apply the top fix", "dig
  deeper"), add `--resume`.
- If no session flag is present, the request is not a clear follow-up, the host can
  ask a concise two-option question, and there is an obvious prior rescue run for
  this backend in the conversation, ask once whether to continue that run or start
  fresh.
- Otherwise add `--fresh`.
- A `--fresh` run is **ephemeral by default** — the reference adds the CLI's
  no-persist flag where one exists, so a one-off rescue leaves no resumable session
  on disk. Keep the session only when the user passes `--persist` (a fresh run they
  intend to continue later). `--resume`/`--conversation` operate on an existing saved
  session and are never ephemeral. The native host backend creates no separate CLI
  session, so this applies only to CLI forwarders.

### Capability

Hand off in default mode. For a CLI backend, pass no permission, sandbox, or bypass
flag — the reference maps this to that CLI's default invocation. For the native host
backend, the subagent runs with its normal permissions. There is no read-only/write
toggle; the backend decides what to touch from the task itself.

### Spawn

**If the requested backend is the host backend — native (default).** Spawn one
subagent through the available subagent/delegation facility and give it the rescue
task directly. It is a fresh, independent instance of the host system; it reasons
natively with no CLI call. Apply the capability and output contract below, and honor
`--model`/`--effort` as a subagent setting when the facility supports it.

Fall back to the host backend's CLI only when the request explicitly needs CLI-only
behavior — `--resume` or `--conversation <id>`, the session persistence a fresh
subagent cannot provide. Then use the forwarder spawn below.

**Otherwise — CLI forwarder.** Spawn one subagent and give it this prompt, with
`<backend>` one of `claude`, `codex`, `gemini`:

```
Read {{SKILL_DIR}}/references/<backend>.md and follow it exactly. Act only as the
thin CLI forwarder it describes — do not inspect the repository, solve the task, or
add analysis of your own. Return the CLI's stdout verbatim as your final message.

Rescue request:
<task text, with the session flags resolved above; --background/--wait stripped>
```

Pass the resolved session and runtime flags through in the task text
(`--resume`/`--fresh`/`--conversation`, `--model`, `--effort`, `--add-dir`, and any
backend-specific flags). The reference maps them to the CLI.

### Output

- Foreground: return the subagent's final output verbatim — the CLI's stdout for a
  forwarder, or the native subagent's result for the host backend. Do not paraphrase,
  summarize, rewrite, or add commentary before or after it.
- Background: return only the host's background handle or status.

## Operating rules

- For single-backend rescue, do not inspect the repo, read files, grep, run the
  CLI, or solve the task yourself — the subagent owns that (a CLI forwarder via its
  reference, or the native host-backend subagent reasoning directly). (Consensus mode
  may read files to embed context into the analyst prompts; that is expected and
  described in the consensus reference.)
- Do not fall back to a direct shell call from the skill. If the target CLI or
  subagent facility is unavailable, the subagent reports it; surface that and stop.
- Do not monitor or poll a background run unless the user later asks for status.
