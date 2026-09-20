# Spec: DevFlow coordinator plugin

## Problem Statement

I delegate implementation to agents, and then I have to go back and check whether they
understood me. Reading their output is re-entry after the fact: by the time I can see the
divergence, it has already been built. So delegation does not buy me flow. It buys me a queue
of things to verify, and verifying them costs the same attention I was trying to protect.

The intent I express in conversation is the thing that gets lost. I say what I want, we work
out what it means together, and then that understanding stays in the conversation while the
work leaves it. Whatever agent picks up the task gets the task, not the understanding.

I also lose it to my own tooling. When a long conversation compacts, the agreements I spent an
hour reaching can come back thinner, or not at all, and I only find out when the agent acts on
something we settled differently.

## Solution

One agent I talk to. It holds what we have agreed, in my own terms, and it carries that into
every piece of work it hands out, so a Worker receives the intent alongside the task.

I never see the machinery. I do not discuss Attention Surfaces, I do not read a Ledger, and I
do not get told about compaction. Those exist so the Coordinator can keep faith with me, not
so I can supervise it keeping faith with me.

The Coordinator's own lapses are caught by deterministic hooks rather than by my attention.
Where a rule must govern behaviour it lives in the Coordinator's system prompt, because that
is the only channel a model treats as authoritative. Where a hook only needs to state a fact,
it states it.

Workers are whatever agents I already have. DevFlow does not ask me to replace them.

## User Stories

1. As a developer, I want to talk to a single agent about a task, so that I do not have to hold a conversation with several agents at once.
2. As a developer, I want that agent to keep track of what we have agreed, so that I do not have to restate decisions I already made.
3. As a developer, I want my own statements recorded as Proposals distinct from the agent's, so that its suggestions never quietly become my requirements.
4. As a developer, I want a Proposal to stay Open until I settle it, so that conversational momentum does not count as agreement.
5. As a developer, I want the Coordinator to notice when a new Proposal conflicts with one I already Accepted, so that it raises the conflict instead of silently replacing my decision.
6. As a developer, I want the Coordinator to quietly retire its own unsettled suggestions when they stop making sense, so that I am not asked to adjudicate its bookkeeping.
7. As a developer, I want the level of detail I used when specifying something to be preserved, so that a decision I made precisely does not come back vague.
8. As a developer, I want the Coordinator to track how much I care about each topic, so that it presses me on the things I want to own and does not press me on the things I do not.
9. As a developer, I want that tracking to stay invisible, so that I never have to learn or discuss the vocabulary of the mechanism.
10. As a developer, I want a Plan Alignment before work is handed out, so that I can see what we agreed without reading code.
11. As a developer, I want to approve a handoff before it happens, so that work never leaves the conversation without my say.
12. As a developer, I want the Coordinator to implement nothing itself, so that its attention stays on me rather than on a diff.
13. As a developer, I want every Worker to receive a Brief, so that it knows what was agreed before it starts.
14. As a developer, I want the Brief scoped to what the task touches, so that a Worker is not handed an hour of conversation it has no use for.
15. As a developer, I want the Brief to carry what is explicitly out of scope, so that a Worker does not helpfully build something I rejected.
16. As a developer, I want the Brief to contain only settled Proposals, so that a Worker never acts on a question I have not answered.
17. As a developer, I want the Brief delivered so that a Worker treats it as binding, so that it cannot dismiss my intent as untrusted context.
18. As a developer, I want the Brief to reach Workers I did not explicitly brief, including review and research agents, so that every agent in the session is working from the same understanding.
19. As a developer, I want to keep using my existing agent definitions as Workers, so that adopting DevFlow does not mean rebuilding my toolkit.
20. As a developer, I want work dispatched in the background, so that I can keep talking while it runs.
21. As a developer, I want the Coordinator to check a finished Worker against what we agreed, so that I do not have to review the work to find out whether it listened.
22. As a developer, I want that check to read what the Worker actually did rather than its own summary, so that a Worker cannot self-certify.
23. As a developer, I want to be told when a Worker diverged, in terms of the agreement it broke, so that I can decide what to do without opening the code.
24. As a developer, I want the Coordinator to tell me immediately when something I just said affects work already running, so that I find out while I can still stop it.
25. As a developer, I want to decide whether to stop that Worker or reconcile afterwards, so that the choice stays mine.
26. As a developer, I want a Worker's discovery to reach me as an ordinary Proposal from the Coordinator, so that I do not have to reason about which agent originated what.
27. As a developer, I want our agreements to survive a long conversation, so that an afternoon of alignment is not lost to a full context window.
28. As a developer, I want that to happen without a file I have to maintain, so that the record does not become another thing I own.
29. As a developer, I want nothing about compaction to appear in my chat when it works, so that the common case is silent.
30. As a developer, I want the agreements restored automatically when compaction fails, so that a failure I did not cause does not cost me the session.
31. As a developer, I want to be told in one sentence when something genuinely could not be recovered, so that I am not misled into thinking the Coordinator still knows something it does not.
32. As a developer, I want that sentence to name the specific gap, so that I can fill it in one reply rather than restating everything.
33. As a developer, I want the Coordinator never to invent an agreement it cannot substantiate, so that a thin recovery is visible rather than plausible.
34. As a developer, I want to opt into DevFlow per session, so that my ordinary sessions are unaffected.
35. As a developer, I want the hooks inactive outside a DevFlow session, so that nothing I did not ask for runs against my other work.
36. As a developer, I want to install this as a plugin, so that its hooks are trusted and I do not have to wire settings by hand.
37. As a developer, I want the plugin to work in a project I have not marked as trusted, so that installation is not silently a no-op.

## Implementation Decisions

**The Coordinator is an agent definition, and it is the only place authority lives.** Its
system prompt carries the Dev Flow discipline (Attention Surfaces, Proposal lifecycle, Plan
Alignment), the Ledger schema, the instruction to reproduce the Ledger when summarizing for
compaction, the obligation to merge a recovered Ledger when told one is damaged, and the rule
about where the Ledger may appear. Nothing that must govern behaviour is placed anywhere else.
This follows ADR 0001 and is the design's load-bearing constraint.

**Activation is per session via the agent flag.** The hooks are declared in the Coordinator's
own definition, so they exist only when that definition is running. There is no global
install and no project-level opt-in.

**Packaging is a plugin.** Plugin-sourced hooks clear the trust gate that silently disables
project-sourced frontmatter hooks in untrusted folders.

**There is no Worker agent type.** Workers are whatever the user already has.

**The Coordinator writes the Brief and a hook enforces it.** The Brief comes from what the
conversation established, which lives only in the Coordinator's context, so no hook can compose
it. The Coordinator writes it under a `## Brief` heading, and a `PreToolUse` hook matched on the
Agent tool denies any dispatch lacking one, handing it back with the reason. See the amendment
to ADR 0001. The hook fails open: an unbriefed dispatch getting through is better than every
dispatch in the session wedging.

**Brief content.** Plan Alignment output filtered to what the task touches. Accepted and
Rejected Proposals only. No Open Proposals, no Proposal IDs, no Attention Surfaces, no
engagement levels. It carries what was agreed and what is explicitly out, in the user's own
established level of detail.

**The Ledger lives in the conversation and is carried through compaction by the summarizer.**
It uses the existing markdown schema with stable `A-###` and `P-###` identifiers and the five
Proposal statuses. It is never written to a file during normal operation and never printed
into ordinary replies.

**Compaction is checked, not trusted.** A `PostCompact` hook runs a deterministic structural
check over the summary: sentinel block present, at least one Proposal, a legal status on each,
every area reference resolving, identifiers unique, and no previously present Proposal having
disappeared relative to the prior compaction summary found in the transcript.

**The check must mirror what the model actually receives.** The harness strips the analysis
section and the summary tags, and keeps everything else including text after the closing tag.
An unterminated analysis section is not stripped at all. A checker that examines only the
summary section produces false losses.

**Repair reads the transcript.** On a failed check, a deterministic extractor pulls the last
good Ledger from the preceding compaction summary entry, every user message since, and the
Coordinator's most recent messages. Per ADR 0002.

**The budget is set by the delivery channel, not by the window.** `UserPromptSubmit`
`additionalContext` is capped near 10,000 bytes, beyond which the harness swaps in a 2KB stub.
So the payload shrinks to fit in a fixed order: the recovered Ledger is never dropped, because
nothing else can reconstruct it; the user's messages come next, because they are what make a
gap nameable; the Coordinator's own messages go first when room runs short, because it can be
asked about those instead. The payload states what it had to leave out.

**The alert is a fact, the duty is in the prompt.** `PostCompact` cannot inject, so it writes
a flag. The next `UserPromptSubmit` returns the recovered material as `additionalContext`,
labelled as possibly stale, and clears the flag. The obligation to merge it lives in the
agent definition. This split is the only arrangement measured to work.

**Nothing else may write that flag.** A model accepts an injected damage claim without
questioning it, so the flag's provenance is a correctness property.

**User-visible behaviour on repair.** Silence when compaction succeeds. One sentence when a
repair was clean. One sentence naming the specific gap when it was not. The Coordinator speaks
about the work and never about compaction, Ledgers or hooks.

**Anti-leak wording is not a refusal mitigation.** A two-arm test showed rewording changes
nothing (5/8 versus 6/8 refusals). Phrase the rule however reads best; do not expect it to
affect compaction reliability.

## Testing Decisions

**One seam: the hook process boundary.** Every hook is a pure function of its stdin JSON plus
the filesystem, producing stdout JSON. Tests feed a hook a recorded stdin payload and a
fixture transcript, and assert on its stdout. No Claude Code process is involved, nothing is
mocked, and the thing under test is the same code that ships.

A good test here asserts on the contract a hook publishes, never on how it parses. For the
checker that means the verdict, not the intermediate structures. For the Brief injector it
means the resulting tool input, including that untouched fields survive the full replacement.
For the repair extractor it means the recovered payload given a known transcript.

Modules tested at that seam: the Ledger checker, the transcript repair extractor, the Brief
injector, and the flag lifecycle across the `PostCompact` and `UserPromptSubmit` pair.

**Prior art is already in the repo.** `scripts/ledger_check.py` and
`tests/fixtures/compact-summaries/` were rescued from the experiments. The five fixtures are
real summaries covering every documented edge case: a complete Ledger after five consecutive
compactions, a refusal, a structurally valid but empty block, a Ledger emitted after the
closing summary tag, and an unterminated analysis section. The checker's verdicts on all five
match the recorded ground truth, so they work as regression tests from day one.

**What is deliberately not tested.** Whether the summarizer reproduces the Ledger, whether a
Worker obeys a Brief, and whether the Coordinator acts on an alert are model behaviours. They
cannot be asserted in a unit test and were established by measurement instead. That evidence
lives in `docs/compaction-findings.md` with its run counts, and it is the reason those
decisions are shaped as they are. Changing one of those decisions means re-measuring, not
re-running the suite.

## Out of Scope

- Retiring the existing prototype under `.agents/skills/dev-flow/`, its `CONFIG.md` and config
  protocol, the `.scratch` context files, and the `flow` branch. The plugin is built fresh and
  the old material is left alone.
- Codex support. Dropped earlier as not worth the duplication.
- Routing bulk pasted content to a Worker so it never enters the Coordinator's window. This is
  a promising response to the refusal problem rather than a patch on it, but it is unvalidated
  and stays an open option.
- Measuring refusal behaviour on models other than Sonnet 5.
- Any model-side mitigation of compaction refusal. Repair is the answer for now.

## Further Notes

**The refusal finding is the sharpest risk.** With turns shaped like bulk data dumps, refusal
was the majority outcome, 11 of 16. A refusal is recorded as a successful compaction and
replaces the whole context with the refusal text, and it cites itself as precedent on later
attempts. So repair is the primary path under realistic conditions, not a backstop. Anyone
weakening the repair loop should read that section of the findings first.

**Everything was measured on Sonnet 5.** A real user on Opus may refuse at a different rate,
or reproduce the Ledger differently. Treat the numbers as evidence that the mechanism works,
not as a prediction of the rate.

**A model's explanation of its own refusal is unreliable.** Refusals quoted the agent prompt's
prohibition as their reason, and removing the prohibition changed nothing. Do not design from
what a model says about itself.
