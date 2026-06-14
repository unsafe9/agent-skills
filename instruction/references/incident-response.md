# Incident-Driven Instructions

Use this reference when a user points at a specific agent mistake and wants to
understand why it happened, prevent it, or turn the lesson into durable
instruction text.

## Workflow

1. Reconstruct the failure from the user's report, conversation text, artifacts,
   and available logs. Separate observed facts from inferred causes.
2. Identify the likely instruction failure mode: missing trigger, ambiguous scope,
   conflicting instructions, stale context, over-specific wording, unchecked
   assumption, weak validation, wrong tool/source preference, or a rule placed on
   the wrong surface.
3. Check whether prose is the right fix. Prefer deterministic enforcement in code,
   tests, linters, hooks, templates, or scripts when that would be more reliable.
4. Choose the narrowest durable surface: nested `CLAUDE.md` for a directory,
   repository `CLAUDE.md` for repo-wide behavior, a skill for reusable conditional
   workflow, an agent prompt for a delegated role, or a hook for event-specific
   injection.
5. Either propose the instruction or edit it directly, matching the user's ask and
   confidence level.

## Generalize the fix

Do not encode only the visible incident. Extract the broader failure mode and write
the instruction so it catches nearby variants. It is acceptable to include one
short line that names the concrete incident as a reminder, but the operative rule
must still follow this skill's normal principles: final-state, terse, host-neutral,
scoped to the right surface, and not a transcript of what just went wrong.

## Draft checklist

- Trigger: when should a future agent apply this?
- Action: what must it do differently?
- Boundary: what should it avoid doing?
- Source hierarchy: which instruction files, tools, or artifacts decide the case?
- Verification: what quick check proves the rule was followed?
