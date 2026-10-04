# DevFlow

One agent you talk to. It holds what you agreed and carries it into the work it delegates, so
you stay in flow instead of reviewing whether the other agents understood you.

## Use it

```
claude --agent dev-flow:devflow
```

Or pick the `dev-flow:devflow` output style (`/output-style dev-flow:devflow`, or the
session's Output style menu in the desktop app). To make it the default, set
`"outputStyle": "dev-flow:devflow"` in `~/.claude/settings.json`.

Nothing is active in an ordinary session.

## What's here

- [`agents/devflow.md`](agents/devflow.md) — the Coordinator: philosophy, practice, and the Ledger schema. Served as both the agent definition and the output style.
- [`skills/recall/`](skills/recall/SKILL.md) — reconstructs the Ledger from conversation history after compaction or session resume.
- `.claude-plugin/` — plugin manifest for the Claude marketplace.
