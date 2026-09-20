# Briefs are delivered by rewriting the dispatch, not by injected context

A Brief must govern what a Worker does, so it has to arrive through a channel the Worker
treats as authoritative. Hook-injected context is not one: Claude Code renders it as a
`<system-reminder>`, and Workers were observed discarding injected constraints on
provenance grounds ("that instruction didn't come from you") even when the constraint was
benign and additive. We therefore deliver the Brief by rewriting the dispatch itself with a
`PreToolUse` hook on the Agent tool, placing the Brief in the Worker's own prompt, where it
is indistinguishable from what the Coordinator wrote.

## Consequences

- `updatedInput` is a full replacement: the hook must echo the entire tool input back with
  its edits applied, or the dispatch fails schema validation loudly and the Coordinator
  cannot recover.
- `SubagentStart` remains useful for delivering *facts* a Worker may read, but never for
  constraints it must obey.
- The general rule this case establishes: hooks deliver facts reliably and cannot deliver
  authority. Anything that must govern behaviour belongs in a prompt, a system prompt, or
  an agent definition.
