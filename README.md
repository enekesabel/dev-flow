## What is DevFlow

DevFlow is a set of behavioral instructions and skills that let engineers concentrate on what
matters: being there for the **Decisions** that matter, while leaving the busywork to agents.

It's constantly evolving as I learn what works and what doesn't.

## Motivation

### Divergence and Convergence

Every piece of work moves between **Divergence** and **Convergence**. Divergence explores:
trying things, investigating, prototyping what could work. Convergence decides: collapsing what
you found into commitments you'll defend over time. With agents, Divergence costs almost
nothing, so the work can expand faster than you can converge it, and Decisions start getting
made without you.

### Flow

**Flow** is the state of being present in the work: challenged but clear, each move connected to
the next. Every move opens **Tension**, a gap between what exists and what could be, and Tension
seeks resolution. Working alone, you feel when it's too much to hold and you converge: name
something, delete a path, write a test. Agents don't feel that. The Tension builds out of sight
and comes back as a review full of Decisions you weren't there for, with context you now have to
reconstruct.

### Staying in the Loop

DevFlow is an attempt to keep you in the loop on the things that matter to you, and to make sure
you get informed when an agent diverges from what you agreed.

## How it works

DevFlow assumes you work with two kinds of agents: **Coordinators** and **Workers**. One kind
you talk to, the other you don't.

Coordinators don't build, and DevFlow applies only to them. Their responsibility is aligning
with you, handing the work out to Workers, and checking the work they've done.

Use smart models for Coordinators.

Coordinators keep a **Ledger** of **Proposals** and Decisions, separating what came from you,
what came from agents, and what came from external sources.

They also pay attention to how engaged you are in each topic. Where you're involved, they keep
you in the loop. Where you don't seem involved, or you've delegated the Decisions, they don't
bother you unless something touches what you own.

Before sending a Worker a **Brief** (a spec, a plan, whatever your workflow dictates or you ask
for), they align with you on the open Proposals that must be resolved to make the Brief
complete. They don't bother you with what's already settled or what doesn't need your attention.

Once the work is done, the Coordinator checks it against the agreed Brief and points out where
the Workers diverged, so you're aware and can course correct.

## What DevFlow isn't

DevFlow isn't an agent coordination framework or SDLC loop. Coordinators delegate through
whatever mechanism you already use, and DevFlow plays well with other skills (for example [Matt
Pocock's](https://github.com/mattpocock/skills)) and frameworks like
[OpenSpec](https://github.com/Fission-AI/OpenSpec). It's just a behavioral layer that keeps your
agents aligned and doesn't dictate how you work.

## Install

In Claude Code:

```
/plugin marketplace add enekesabel/dev-flow
/plugin install dev-flow@dev-flow
```

Installing changes nothing in an ordinary session. DevFlow is only active when you start it.

## Start DevFlow

```
claude --agent dev-flow:devflow
```

Or pick the `dev-flow:devflow` output style (`/output-style dev-flow:devflow`, or the session's
Output style menu in the desktop app). To make it the default, set
`"outputStyle": "dev-flow:devflow"` in `~/.claude/settings.json`.

## Skills

DevFlow comes with a set of skills: some apply to DevFlow only, others work on their own and
bring software development best practices. A Coordinator may invoke any of them automatically
while you work with it. Outside DevFlow, you have to invoke them explicitly.

| Skill | Use it for | Outside DevFlow |
| --- | --- | --- |
| [system-architecture](skills/system-architecture/README.md) | Documenting a system's architecture, with evidence, and drawing it as a diagram that switches between environments. | `/dev-flow:system-architecture` |
| [recall](skills/recall/SKILL.md) | Restoring what you and the Coordinator agreed, after compaction or a resumed session. | DevFlow only |

## What's coming next

- **software-design**: how your system manifests in code: modules, layers and how they're
  organized.
- **test-design**: tests that protect one clear requirement, at one level, through the right
  seam, and change only when that requirement changes.
