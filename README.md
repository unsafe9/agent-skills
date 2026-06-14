# agent-skills

A curated collection of agent skills by [unsafe9](https://github.com/unsafe9),
hand-picked from a personal skill workbench and published here for external sharing.

Skills are kept tool/host-neutral where possible, so they work across agent hosts
(Claude Code, Codex, and other [skills CLI](https://github.com/vercel-labs/skills)-compatible agents).

## Install

Use the [skills CLI](https://github.com/vercel-labs/skills):

```bash
# Install every skill in this repo
npx skills add unsafe9/agent-skills

# Install a specific skill
npx skills add unsafe9/agent-skills --skill <skill-name>

# Preview what's available without installing
npx skills add unsafe9/agent-skills --list
```

By default the CLI installs into your project and symlinks the skills into your agent
directories. Add `-g` for a global (user-level) install, or `--copy` to copy files
instead of symlinking.

## Available Skills

<!-- catalog:start -->
| Skill | Description |
| ----- | ----------- |
| [`alfred-workflow`](skills/alfred-workflow/) | Author Alfred 5 workflows as code by writing the native info.plist XML — object graph, connections, canvas layout (uidata), user configuration — then validating, packaging into .alfredworkflow, and installing. |
<!-- catalog:end -->
