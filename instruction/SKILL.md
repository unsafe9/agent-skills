---
name: instruction
description: "Write, edit, or review durable agent instructions so they read well to a fresh agent at startup. Use whenever work touches CLAUDE.md, AGENTS.md, nested directory-scoped CLAUDE.md or AGENTS.md files, a shared skill (SKILL.md), an agent or subagent prompt, an instruction-injecting hook, or any other startup/context/system prompt. Also use when an agent made a mistake and the user wants the cause analyzed, a preventive instruction proposed, or instruction text written."
---

# Instruction

You are writing or revising text an agent reads as context before it acts. The
reader is a fresh LLM agent with no memory of why the text exists and a limited
context budget — optimize for what that agent needs to act correctly, not for a
human reading the diff.

Use `{{SKILL_DIR}}` to mean the directory containing this `SKILL.md`.

## Reference routing

- For incident-driven work where an agent made a mistake and the user wants a
  cause analysis, prevention strategy, or new instruction, read
  `{{SKILL_DIR}}/references/incident-response.md`.

## Final state, not history

Document the final state an agent needs at startup. Do not record one-off edit
history, migration notes, or rationale that only explains why the current change
was made. The reader was not present for the change and gains nothing from it; that
context belongs in the commit message or PR, not the living instruction.

## Lead with what code can't tell you

Code is the source of truth, and the agent can read it: directory layout,
implementations, signatures, and call sites it discovers on its own, fast. Don't
restate them — a catalog of facts the agent could find itself goes stale and burns
context. Spend the words on what a code read can't recover: the overview, design
intent, goals, operating assumptions, and the tradeoffs behind a choice — for
example the architecture and deployment shape, how components communicate, and the
design principles the code must honor but never states (statelessness, a
stack-neutral interface chosen for extensibility).

When you must point at code, point — don't paste. Name a stable file, ownership
boundary, or command; avoid volatile snippets that go stale and mislead, and keep
any mention short, descriptive, and tied to the instruction.

The same holds for commands an agent needs to work fast: if an authoritative source
exists, point to it — say to read the `Makefile`, the `scripts/` directory, or
`package.json` scripts — instead of copying command lists that drift. Spell a
command out inline only when nothing else records it.

## Write for an LLM reader

The reader spends tokens on every line, so be terse. Say it once, in the fewest
words that stay unambiguous; cut throat-clearing, hedging, and restated context.
Density beats completeness — a short instruction that actually gets read and applied
beats an exhaustive one that buries the point. Apply the same restraint to structure:
before opening a new section for a rule, check whether it fits an existing one as a
bullet or a clause — grow a section rather than multiply them.

Default to English for the instruction text and any output you produce — it's the
model's strongest and most token-efficient language — even when the surrounding
conversation is in another language.

## Stay host-neutral

Keep shared instructions host-neutral unless a section is explicitly documenting a
host-specific adapter. Name the capability, not one host's tool for it, so the
instruction survives a host swap:

- "available web search/fetch tool" instead of `WebFetch`
- "available file-editing tool" instead of `Write`
- "available subagent/delegation facility" instead of `Agent`
- "available follow-up/user-question facility" instead of `AskUserQuestion`
- `{{SKILL_DIR}}` instead of `${CLAUDE_SKILL_DIR}` or an absolute path

Do not prescribe meta-discovery steps like "use a tool-search tool to find the
right tool, then use that tool". State the needed capability, the source
preference, and the selection criteria; let the current host discover and choose
its own tools.

Likewise, when authoring a skill, don't wire in a dependency on another named
skill unless the user asked for that coupling. Name the underlying capability or
tool and use it directly, so the skill stands alone if the other skill is
renamed, moved, or absent.

## Generalize from incidents

When a request is prompted by a specific incident, do not encode only that exact
case as a narrow rule — the next failure will look slightly different and slip past
it. Extract the broader concept or failure mode. Add a one-shot or few-shot example
only when it genuinely clarifies the intended behavior: examples bias the model hard
toward their specifics, so reach for one only when necessary and keep it neutral and
representative rather than narrow.

## Instruction file scope

Before choosing a file, identify the scope of the rule. For a repository-wide
rule, use the repository instruction file. For a subtree-specific rule, prefer a
nested instruction file in that directory so the special case does not pollute
global context.

When instruction work targets a directory, check that directory and relevant
ancestors for `CLAUDE.md` and `AGENTS.md` before editing or proposing text. If one
is a symlink to the other, treat them as one source. If both are real files, read
both and preserve their intent instead of silently collapsing them.

When creating a new instruction file, default to `CLAUDE.md`. Create `AGENTS.md`
only when requested, and make it a symlink to `CLAUDE.md` when the filesystem
supports symlinks. Apply the same default to nested instruction files.

## Where does this belong

Match the content to the surface so each stays in scope:

- **CLAUDE.md / AGENTS.md** — durable always-on background and operating
  assumptions every agent needs at startup.
- **Nested CLAUDE.md / AGENTS.md** — scoped rules for files under one directory,
  especially local exceptions or ownership boundaries that should not load
  globally.
- **A skill (`SKILL.md`)** — reusable workflow, evidence standards, source
  preferences, and output shape, loaded only when its trigger fires. Put
  host-specific command or tool examples in a clearly labeled host-specific adapter
  section, not mixed into the portable body.
- **An agent/subagent prompt** — role, scope, and constraints for one delegated job.
- **A hook** — the narrow instruction or guard injected at a specific event.

And before any of these: if the rule is a coding convention a linter, formatter,
type system, or structural change can enforce deterministically, it belongs in that
tooling, not in prose the model must remember every time. Check for that first.
