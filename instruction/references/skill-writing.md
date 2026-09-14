# Writing Skills

## Description

The description guides selection before the body is read, so give the primary use
case first and leave execution details in the body. Cover distinct situations that
should select the skill, retaining the terms users actually use. Collapse synonyms
that only rename the same situation. A shorter description earns its savings only
if it still distinguishes the intended requests from nearby unrelated ones.

## Invocation

Preserve the existing invocation policy; new skills default to automatic discovery.
A skill the agent should select during ordinary work needs a model-facing description.
Use explicit-only invocation when the user wants to choose each invocation, weighing
the burden of remembering the skill against the context needed to advertise it.
Keep user-only skills available for explicit user invocation while excluding them from
model discovery and loading. Keep a concise human-facing summary for an explicit-only
skill.

Translate the chosen policy into verified settings for each supported host. Invocation
and context-loading controls are not universal frontmatter fields.

## Shared references

Keep shared reference material in a plain file when several workflows need it. Give
it a separate skill only when independent discovery justifies another description.
Depend on another named skill only when the user has requested that coupling;
otherwise name the underlying capability or link to a maintained reference so the
skill can stand alone.
