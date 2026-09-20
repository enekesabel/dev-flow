# Briefs are delivered by rewriting the dispatch, not by injected context

A Brief must govern what a Worker does, so it has to arrive through a channel the Worker
treats as authoritative. Hook-injected context is not one: Claude Code renders it as a
`<system-reminder>`, and Workers were observed discarding injected constraints on
provenance grounds ("that instruction didn't come from you") even when the constraint was
benign and additive. We therefore deliver the Brief by rewriting the dispatch itself with a
`PreToolUse` hook on the Agent tool, placing the Brief in the Worker's own prompt, where it
is indistinguishable from what the Coordinator wrote.

## Amendment: the hook enforces the Brief, it does not write it

Building this exposed an assumption the original decision rested on. Rewriting the dispatch
requires knowing the Brief, and the Brief is Plan Alignment output scoped to the task, which
lives only in the Coordinator's context. A hook reads stdin and the filesystem, and the Ledger
is in neither. So the hook cannot compose a Brief.

The conclusion above still holds: the Brief must arrive in the Worker's own prompt, because
injected context does not govern. What changes is who puts it there. The Coordinator writes the
Brief under a `## Brief` heading, and the `PreToolUse` hook denies any dispatch that lacks one,
handing it back with the reason. The hook protects the Coordinator from its own lapse rather
than doing the work for it, which is the role hooks hold everywhere else in this design.

## Consequences

- `updatedInput` is a full replacement: the hook must echo the entire tool input back with
  its edits applied, or the dispatch fails schema validation loudly and the Coordinator
  cannot recover.
- `SubagentStart` remains useful for delivering *facts* a Worker may read, but never for
  constraints it must obey.
- The general rule this case establishes: hooks deliver facts reliably and cannot deliver
  authority. Anything that must govern behaviour belongs in a prompt, a system prompt, or
  an agent definition.
