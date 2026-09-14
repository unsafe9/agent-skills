---
name: instruction
description: "Write, edit, or review durable agent instructions in CLAUDE.md, AGENTS.md, skills, agent prompts, or context-injecting hooks. Also use to analyze agent mistakes and propose prevention."
---

# Instruction

You are writing or revising text an agent reads as context before it acts. The reader
is a capable model that has no memory of why the text exists and pays tokens for every
line — a fresh colleague, not a novice. Optimize for what that reader needs in order to
act correctly, not for a human reading the diff.

Use `{{SKILL_DIR}}` to mean the directory containing this `SKILL.md`.

## Reference routing

- When creating, editing, or reviewing a skill, read
  `{{SKILL_DIR}}/references/skill-writing.md` for descriptions, invocation policy,
  and shared references.
- For incident-driven work where an agent made a mistake and the user wants a cause
  analysis, prevention strategy, or new instruction, read
  `{{SKILL_DIR}}/references/incident-response.md`.

## Start with the irreducible instruction

Instructions supply what another capable agent cannot infer: explicit intent and taste,
local tradeoffs, scope and permission boundaries, exceptions to the sensible default,
and the required standard of evidence. Treat the user's request as evidence of what
matters to them, not as an invitation to invent every sensible companion rule. If a
line is only an immediate common-sense elaboration or would not change the reader's
next action, omit it.

For a new instruction or skill, start with the smallest useful draft: normally one or
two sentences, and no more than one short paragraph unless the user has already given
several independent constraints. Do not pre-create sections, checklists, examples,
references, or exhaustive workflows. Add structure only when the accumulated content
can no longer be read clearly as one paragraph.

Grow the instruction only from evidence: the user adds intent or a preference, real
usage exposes ambiguity or failure, a non-obvious invariant must survive, or risk
requires an explicit guardrail. Expand an existing principle before adding another
rule; extract a reference or script only after conditional detail or repeated mechanics
has genuinely accumulated.

When revising an existing file, suspect bloat or contradiction before assuming it is
incomplete. Remove rules that no longer change behavior, repeat each other, or conflict
with a newer one. A revision that only adds is usually the wrong revision.

For recurring failures or consequential rule changes, resolve uncertainty about a
rule's value by comparing representative runs with and without it. Judge the resulting
behavior; clearer wording alone does not establish improvement.

Write the surviving lines tight: say it once, in the fewest words that stay
unambiguous, and cut throat-clearing, hedging, and restated context. Shorten by
dropping what wouldn't change the reader's next action, never by compressing prose into
fragments, abbreviations, or arrow chains — an unreadable instruction is not a short
one. Default to English even when the surrounding conversation is in another language;
it is the model's strongest and most token-efficient language.

## State the principle, not the enumeration

One sentence naming the behavior you want covers the whole family of cases. A list
naming each case covers only the ones you thought of, and reads as a checklist to
satisfy rather than a standard to meet. Write at the level of the concept, not the
incident that prompted it.

Give the reason where it isn't obvious. A clause of intent lets the reader generalize
to the case you didn't foresee, and usually replaces several rules.

Prefer goal and constraints over procedure. Spell out an ordered sequence only where
the order is load-bearing: an external system demands it, a step is destructive, or
skipping it corrupts the result silently. Step-by-step scripts for work the model can
plan itself burn context and lower the quality of what comes back. Where completion is
ambiguous, define an observable result and the scope it must cover.

Reach for an example only when the wanted behavior resists description. Examples bias
hard toward their specifics, so keep it to one neutral, representative case.

## Don't script the model's thinking

Instruct on outcome and constraints, not on how the reader should think. Never ask an
agent to transcribe, echo, or narrate its internal reasoning as output — it spends the
answer on restatement and can trip refusal handling. Mandated deliberation rituals
(rate every option, always list three alternatives, restate the request before
answering) fail the same way: they cost tokens and lock a capable reader into a worse
process than it would have chosen. Ask for the conclusion, the evidence behind it, and
the uncertainty that remains. When structure genuinely matters, specify the shape of
the deliverable, not the thinking that produces it.

## Final state, not history

Document the final state an agent needs at startup. Do not record one-off edit history,
migration notes, or rationale that only explains why the current change was made. The
reader was not present for the change and gains nothing from it; that context belongs
in the commit message or PR, not the living instruction.

## Lead with what code can't tell you

Code is the source of truth, and the agent can read it: directory layout,
implementations, signatures, and call sites it discovers on its own, fast. Don't
restate them — a catalog of facts the agent could find itself goes stale and burns
context. Spend the words on what a code read can't recover: the overview, design
intent, goals, operating assumptions, and the tradeoffs behind a choice — for example
the architecture and deployment shape, how components communicate, and the design
principles the code must honor but never states (statelessness, a stack-neutral
interface chosen for extensibility).

When you must point at code, point — don't paste. Name a stable file, ownership
boundary, or command; avoid volatile snippets that go stale and mislead. The same holds
for commands: if an authoritative source exists, say to read the `Makefile`, the
`scripts/` directory, or `package.json` scripts instead of copying lists that drift.
Spell a command out inline only when nothing else records it.

## Organize references by use

Keep guidance needed across the document's uses in the main file. Move substantial
detail needed only in particular situations behind a reference that names those
situations. Split by use, not by length alone; a short document may need no split.
Keep a concept's definitions, rules, and caveats together so reading one brings the
others into view.

Each reference should identify what it contains and when to read it. If required
material is being missed, clarify that trigger before moving the material inline.
Keep each rule in one authoritative place so a change does not require synchronized
edits to the entrypoint and its references.

## Stay host-neutral

Keep shared instructions host-neutral unless a section is explicitly documenting a
host-specific adapter. Name the capability, not one host's tool for it, so the
instruction survives a host swap:

- "available web search/fetch tool" instead of `WebFetch`
- "available file-editing tool" instead of `Write`
- "available subagent/delegation facility" instead of `Agent`
- `{{SKILL_DIR}}` instead of `${CLAUDE_SKILL_DIR}` or an absolute path

Don't prescribe meta-discovery steps like "use a tool-search tool to find the right
tool, then use that tool". State the needed capability, the source preference, and the
selection criteria; let the current host discover and choose its own tools.

Stay out of the tool call itself, too. Search flags, glob patterns, which directory to
sweep first, how many results to read back — the reader picks better mechanics than your
recipe, and a recipe written against one toolset rots when the tools change. Say what
has to be found and what makes a hit relevant, then stop. Naming a location is not the
same as scripting a search: point at where something lives when that is a local fact
worth carrying, and leave the traversal alone.

## Choose the surface

Match content to surface so each stays in scope:

- **CLAUDE.md / AGENTS.md** — durable always-on background and operating assumptions
  every agent needs at startup.
- **Nested CLAUDE.md / AGENTS.md** — rules scoped to one subtree that should not load
  globally.
- **A skill (`SKILL.md`)** — reusable workflow, evidence standards, source preferences,
  and output shape, loaded only when its trigger fires.
- **An agent/subagent prompt** — role, scope, and constraints for one delegated job.
- **A hook** — the narrow instruction or guard injected at a specific event.

Before any of these: if a linter, formatter, type system, test, or structural change
can enforce the rule deterministically, it belongs in that tooling, not in prose the
model must remember every time.

Check the target directory and relevant ancestors for existing `CLAUDE.md` and
`AGENTS.md` before editing or proposing text. If one is a symlink to the other, treat
them as one source; if both are real files, preserve both intents instead of silently
collapsing them. New files default to `CLAUDE.md`, with `AGENTS.md` created only on
request and as a symlink where the filesystem supports it.

## Write nested files for the arriving reader

A nested file loads only once an agent is already inside its directory, and then stays
in context for the rest of the session. It is an instruction that fires on arrival, not
a README: no tour of what the directory holds, and none of the pointers that would send
someone here. Write what the arriving reader needs before touching these files — the
delta from the parent, with a local exception stated as one — and scope each rule to the
subtree in its own wording, or it keeps steering work that has moved on. Place the file
at the highest directory where its rules hold.
