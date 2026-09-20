# What we measured about Claude Code hooks and compaction

Findings from nine experiment campaigns against Claude Code 2.1.278, run headless with an
isolated working directory, explicit `--settings`, `--agents` and `--setting-sources ""`.
Test runs used Sonnet 5, except the first two campaigns which used Haiku 4.5. Total spend on
the runs was $35.13.

Every claim below carries its run count. Claims without one come from reading the binary's
strings rather than from a live run, and are marked as such. Anything not listed here was not
measured.

## The central finding

**Hooks deliver facts reliably and cannot deliver authority.**

Hook-injected text renders to the model as a `<system-reminder>`, and models consistently
treat it as something to weigh rather than obey. Three independent demonstrations:

- A worker given a conflicting constraint with an escape clause produced the null action.
- Without the escape clause it said *"injected context isn't a valid substitute for your own
  instructions, so I'm disregarding it."*
- A benign, purely additive constraint was still refused on provenance grounds: *"That
  instruction didn't come from you."*

And a coordinator handed its own restored ledger through a hook: *"I'm not treating that
DEVFLOW LEDGER block as authoritative, it's injected content riding in on a system-reminder
again."* It could quote the block perfectly and would not act on it.

The inverse also holds and is what makes the design work: a bare **fact** delivered by a hook,
paired with an obligation that already lives in the agent's system prompt, **is** acted on.
5/5 runs rebuilt a ledger correctly from such an alert, none dismissed it.

One caveat with teeth: a false damage claim was accepted and restated as fact without
question. The channel that makes the alert work makes it unverifiable from inside the model.

## Channels that reach the compaction summarizer

Three, and only three:

1. `PreCompact` hook stdout, appended to the summarizer prompt as an "Additional Instructions:" section.
2. The agent system prompt.
3. `CLAUDE.md`, which requires `--setting-sources` to include `project`.

No `settings.json` key injects summarizer text (from binary strings).

**They are not equivalent.** `PreCompact` stdout is treated as injection and backfires: the
summarizer discarded the instruction and the ledger with it, while a control run carrying no
instruction preserved the ledger. The agent system prompt was **never** treated as injection
across 47 compactions.

## Ledger fidelity when a summary is produced

With the schema and the emit instruction in the agent system prompt:

- Complete and correct in 9/9 runs, all 9 ground-truth proposals, including two that changed
  status mid-conversation.
- Zero fabricated proposal IDs across 47/47 summaries.
- One run carried a correct 9-proposal ledger through **5 consecutive compactions** with the
  scope text verbatim.
- Degradation, when it happens, is loss and never fabrication (47/47). Two runs emitted a
  structurally valid but empty block: the schema was obeyed with nothing left to put in it.

Earlier campaigns did see fabrication, when the ledger was emitted by the assistant into the
conversation rather than produced by the summarizer under instruction.

## Refusals

The summarizer sometimes replies with a refusal instead of a summary. This is the dominant
failure mode.

- Rate: 3/12 first compactions in the controlled campaign. Roughly 8/15 in earlier, less
  controlled ones.
- **Cause, isolated by single-variable test:** the shape of the user turn immediately
  preceding compaction. A bulk data dump gave 3/4 refusals. On-topic prose of the same size,
  everything else identical, gave 0/4.
- Refusals name two things in their own text: the compaction directive arriving "tacked onto a
  620-line wall of unrelated filler text, which is a classic injection pattern", and the agent
  prompt's own prohibition wording, quoted back as *"I have not printed the DevFlow Ledger in
  this reply."*
- **A refusal is recorded as `compact_result: success`** and replaces the entire context with
  the roughly 500-character refusal reply. It destroys the session, not one summary.
- It is self-reinforcing. Later compactions cite the earlier refusal as precedent for
  refusing again.

**Rewording the prohibition does not help.** A two-arm test, identical in every respect except
the anti-leak clause, with bulk-dump filler in both arms:

| arm | wording | refusals |
|---|---|---|
| A | prohibition ("never print the ledger in ordinary replies") | 5/8 |
| B | positive ("the ledger belongs in compaction summaries and in a direct request") | 6/8 |

At n=8 per arm the difference is noise. The refusal is driven by the preceding turn's shape,
not by the agent prompt's phrasing, even though refusals quote that phrasing when explaining
themselves. Treat what a refusal says about its own reasons as unreliable.

The severity this implies: with dump-shaped turns, refusal was the **majority** outcome
(11/16). Repair is not an edge-case backstop, it is the primary path under those conditions.

## Hook events and ordering

- `PostCompact` fires on auto compaction (4/4), **only on successful compactions**, carrying
  `trigger` and `compact_summary`.
- `SessionStart` with `source: "compact"` fires **~40ms before** `PostCompact`. Detect-then-repair
  cannot close in one cycle.
- `SessionStart(compact)` cannot read the fresh summary from `transcript_path`; it is not
  flushed yet.
- `SessionStart(compact)` `additionalContext` **does** reach the post-compaction window,
  visible in the transcript as a `hook_additional_context` attachment.
- `PostCompact` has **no injection variant** (from binary strings).
- Injection at `SessionStart` with `source: "startup"` does not survive compaction.

Events that can return `additionalContext`: Notification, PostModelSwitch, PostToolBatch,
PostToolUse, PostToolUseFailure, SessionStart, Setup, Stop, SubagentStart, SubagentStop,
UserPromptExpansion, UserPromptSubmit. `PreCompact` and `PostCompact` cannot.

## What the model actually sees of a summary

`compact_summary` is the **raw** summarizer output including its `<analysis>` section. The
harness then:

- strips the `<analysis>` section,
- strips the `<summary>` and `</summary>` **tags**,
- and **keeps everything else, including text after `</summary>`**.

One run placed the entire ledger after the closing tag and it reached the model intact. An
**unterminated** `<analysis>` is not stripped at all, and the whole output reaches the model.

Any checker that examines only the `<summary>` section will score both cases as losses.

## Compaction triggering

- `autoCompactWindow` is the settings key. Range 100k to 1M.
- Documented threshold: `window - min(maxOutputTokens, 20000) - 13000`.
- **Observed reality with a 100k window: 63,484 to 85,480 `pre_tokens`** across 47 compactions.
  Do not build anything assuming a precise trigger point.
- A single very large user turn can cause several compactions within that one turn (3 observed).

## What survives compaction

- The stock compaction prompt instructs the summarizer to "List ALL user messages". Content in
  **user** turns survived verbatim 3/3.
- Content emitted by the **assistant** into the conversation was lost: fabricated after the
  first compaction, gone after the second.
- `transcript_path` holds **one `isCompactSummary` entry per compaction** (verified 5/5 and
  3/3), storing the model-visible form with analysis stripped and tags removed. Prior ledgers
  parse straight out of them, which is what makes cross-compaction repair possible without a
  snapshot file.
- Measured composition of one real design session: 63% conversation text, 27% tool results,
  10% tool calls. A coding session would skew the other way.

## Brief delivery to workers

- `SubagentStart` declared on the main agent fires on subagent spawn, and its
  `additionalContext` reaches the subagent as a real attachment before its first turn (proven
  with tools disabled, `tool_uses: 0`). It delivers facts, not authority.
- `PreToolUse` with matcher `"Agent"` (alias `"Task"`) can rewrite the dispatch.
  `updatedInput` is a **full replacement**: echo the entire tool input back with edits applied,
  or it fails schema validation **loudly**. Verified by forcing `run_in_background: false`.
- `PostToolUse` `updatedToolOutput` must be an **object matching the tool's output schema**. A
  plain string fails **silently**.
- Matchers on `SubagentStart` / `SubagentStop` are optional and selective by agent type.
- Agent-declared `PostToolUse` hooks are **session-wide**, firing for subagent-internal tool
  calls too. Discriminate with `agent_type`.

## Dispatch and return

- Async is the practical default: 3/3 dispatches went async when unspecified.
- Async returns arrive as plain **user text** containing a `<task-notification>` with the full
  result, task id and originating tool-use id. **`UserPromptSubmit` fires for it.**
  `Notification` does not.
- The `source` field on `UserPromptSubmit` is **never emitted** in 2.1.278 (compiled out).
  Detect wakeups by sniffing `prompt` for `<task-notification>`.
- **`UserPromptSubmit` `additionalContext` is capped at about 10,000 bytes.** 10,000 is
  delivered inline; 10,020 is replaced by a `<persisted-output>` stub with a 2KB preview and a
  file path, so most of the payload never reaches the model. Anything handed back through this
  channel has to fit, which is a far harder limit than the context window.
- `UserPromptSubmit` `decision: "block"` suppresses the whole wakeup; the reason goes to the
  output stream, not the model.
- Foreground dispatch puts the `PostToolUse` output and the tool result in the **same user
  turn** before the coordinator's next message. No gap.
- `Stop` with `{"decision":"block","reason":"..."}` genuinely blocks turn end, but fires
  **after** the assistant text has already streamed. `stop_hook_active` is advisory, there is
  **no harness loop cap**, and the hook must self-release. Reading `last_assistant_message`
  works for that.
- `SubagentStop` `additionalContext` does **not** reach the coordinator. It feeds back to the
  **subagent** and re-runs it: 9 firings, 8 redundant repeats, 17k wasted tokens.
- `TaskCompleted` is not usable for local subagent dispatch.

## Checks that work, and ones that don't

For deciding whether a block survived a summary:

- **Per-line containment works.** Every non-blank snapshot line must appear as a substring of
  the summary. Matched ground truth 4/4.
- Whole-block string matching **false-alarms 3/3**, because the summarizer reflows whitespace.
- Token-only containment **misses altered decision text** while keywords survive, which is the
  failure that matters most.
- Sentinels must stand **alone on their own line**. A sentinel merely named in prose
  ("wrapped in BEGIN/END sentinels") is not a block, and scoring it as one produced false
  verdicts twice.

A structural checker over the schema (block present, at least one `P-###`, legal `Status:` on
every proposal, every `Area:` resolving to a present `A-###`, unique IDs, plus a
cross-compaction check that no previously present `P-###` disappeared) agreed with hand
judgement on 47/47 collected summaries and 11/11 synthetic adversarial cases.

## Trust gate

Frontmatter hooks originating from `projectSettings` are **silently skipped** in untrusted
folders, visible only via `--debug-file`. `--dangerously-skip-permissions` does not satisfy
the gate. Trusted sources per the binary: `plugin`, `policySettings`, `built-in`, `builtin`,
`bundled`, plus `userSettings` and `flagSettings`.

This is why shipping as a plugin matters: a plugin's hooks are trusted where a project's
are not.

## Harness traps, if anyone re-runs this

Each of these cost at least one wasted campaign.

- `--disallowed-tools` is variadic and swallows a positional prompt. Pass the prompt on stdin
  and give the tool list comma-separated.
- macOS has no `timeout`. Bound runs with `--max-budget-usd`.
- **Random-word filler makes the summarizer hard-fail.** Filler must be coherent.
- **Imperative text in filler hijacks the summarizer.** Filler must be declarative.
- **Bulk data-dump filler causes refusals.** Filler must read as part of the conversation.
- **A model under test can read the hook script off disk and report a result it inferred
  rather than observed.** Disable its tools and verify against hook logs and the transcript.
- `CLAUDE_CONFIG_DIR` cannot be isolated on macOS: auth lives in the Keychain and an isolated
  dir yields "Not logged in". Use the default config dir while writing no real config.
- `total_cost_usd` in stream-json output is **cumulative per session**. Summing it per turn
  over-counts by roughly 4x. Take the last value per session.
- The sandbox classifier blocks credential-inspection paths, which prevented one campaign from
  completing.
