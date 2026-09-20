# DevFlow

One agent you talk to. It holds what you agreed and carries it into the work it delegates, so
you stay in flow instead of reviewing whether the other agents understood you.

## Use it

```
claude --agent devflow
```

Nothing is active in an ordinary session.

## What's here

- `agents/devflow.md` — the Coordinator
- `hooks/` — Brief enforcement, the compaction check, and recovery
- `docs/` — the design, and the measurements it rests on

```
python3 -m unittest discover -s tests
```
