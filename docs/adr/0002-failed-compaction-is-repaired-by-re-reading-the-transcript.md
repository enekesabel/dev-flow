# A failed compaction is repaired by re-reading the transcript

The Ledger normally survives compaction because the Coordinator's agent definition instructs
the summarizer to reproduce it, and that channel is treated as authoritative: across 47
measured compactions, every summary that was produced carried the Ledger complete, with no
fabricated entries. The failure that remains is the summarizer refusing to summarize at all.
A refusal is recorded as a successful compaction and replaces the entire conversation with
the refusal text, so it destroys the session rather than losing one summary. We repair it by
reading the transcript file, which compaction does not touch: a script extracts the last good
Ledger from the preceding `isCompactSummary` entry, every user message since, and the
Coordinator's most recent messages up to a token budget, and a `UserPromptSubmit` hook
delivers all three as fact while the obligation to merge them lives in the agent definition.

## Consequences

- The budget is set by the delivery channel, not by the context window. `UserPromptSubmit`
  `additionalContext` is capped near 10,000 bytes, beyond which the harness substitutes a 2KB
  stub. So the payload shrinks in a fixed order: the Ledger never, the user's messages next,
  the Coordinator's own messages first. In practice the Coordinator's messages rarely fit, and
  the payload says what it left out.
- User messages are recovered in full because they are small and because they index the gaps:
  an approval with no matching Proposal proves a decision was made after the last good Ledger.
- What cannot be reconstructed gets one sentence to the user naming the specific gap. Anything
  the user said themselves, or reacted to specifically, does not need asking about.
- Recovery is deterministic on purpose. A Worker sent to read the transcript would be deciding
  what the user agreed to, which is the one job the Coordinator does not delegate.
- Known upgrade path: the Coordinator's messages are currently selected by recency, which is a
  crude proxy for relevance. Having a model choose which of them actually carry Proposals would
  recover more within the same budget. Not worth building until real sessions show recency
  failing.
