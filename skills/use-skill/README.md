# use-skill

Lets an agent run a skill that only you can invoke, when you name it in plain words.

Many published skills are manual-only (in Claude Code, `disable-model-invocation: true`), so
they start only when you type their slash command. That works while you type to one agent. It
breaks when you hand work off: you tell a coordinator that the worker should use your
architecture skill, and the worker can't, because the harness hides a manual-only skill from
agents.

use-skill treats your naming the skill as the invocation. The agent finds the skill's file,
fills in what invocation would have filled in (arguments, the skill's folder, the output of its
shell commands), tells you which file it is running, and follows it.

## Use it

Install the plugin as described in the [repository README](../../README.md), then name the
skill in plain words, to your agent or in a handoff:

```
Use my improve-codebase-architecture skill on the billing module.
```

```
Hand this to a worker, and have it use the tdd skill.
```

Ask "which skills can only I invoke?" to see them listed.

## What it doesn't do

- It never picks a skill on its own. It runs the one you named, and asks when more than one
  matches.
- It finds skills installed where the agent runs. A cloud session doesn't see skills that live
  only on your laptop.

The details are in [SKILL.md](SKILL.md).
