# DevFlow

One agent you talk to. It holds what you agreed and carries it into the work it delegates, so
you stay in flow instead of reviewing whether the other agents understood you.

## Use it

```
claude --agent dev-flow:devflow
```

Or pick the `dev-flow:devflow` output style (`/output-style dev-flow:devflow`, or the
session's Output style menu in the desktop app). The style carries the same instructions but
no hooks (the style is prompt-only). To make it the default, set `"outputStyle": "dev-flow:devflow"` in
`~/.claude/settings.json`.

Nothing is active in an ordinary session.

## What's here

- `agents/devflow.md` — the Coordinator, served as both the agent and the output style
