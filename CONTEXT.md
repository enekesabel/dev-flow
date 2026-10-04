# DevFlow

DevFlow keeps a developer in flow while implementation is delegated. The developer converses with one agent; that agent carries their intent into work performed by other agents, so the developer never has to reconstruct decisions they did not make.

## Language

### Agents

**Coordinator**:
The single agent the user converses with. It holds the user's intent, composes work for Workers, and decides what reaches the user.
_Avoid_: main agent, orchestrator, manager, primary

**Worker**:
An agent that performs delegated work while the user is not present.
_Avoid_: AFK agent, subagent, subcontractor

### Intent

**Proposal**:
A candidate direction for the work, attributed to whoever originated it and carrying a status the user controls.
_Avoid_: suggestion, option, requirement

**Attention Surface**:
A topic the Coordinator tracks, together with how much the user wants to own decisions within it. Internal machinery: the Coordinator never discusses Attention Surfaces with the user.
_Avoid_: area, topic, focus area

**Ledger**:
The complete record of Proposals and Attention Surfaces for one conversation. What the Coordinator must carry intact from the first exchange to the last.
_Avoid_: context file, state, memory

**Plan Alignment**:
The ordered presentation of Proposals that establishes what the user and the Coordinator have agreed.
_Avoid_: recap, summary, sync

**Brief**:
The intent a Worker receives alongside its task: Plan Alignment output, scoped to what that task touches. It carries what was agreed and what is explicitly out, never the tracking apparatus and never an unresolved Proposal.
_Avoid_: context dump, handoff doc, spec
