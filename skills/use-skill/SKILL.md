---
name: use-skill
description: Use when the user names a skill, by its name or by what it does, that is missing from your skill list or that the Skill tool refuses, whether they name it to you directly or in a Brief you were handed. Also when the user asks which skills only they can invoke.
---

# Use Skill

A **user-invoked** skill sets `disable-model-invocation: true` in its frontmatter. Claude Code
keeps it out of your skill list and the Skill tool refuses it, so it normally starts only when
a person types `/name`. A person naming it in plain words carries the same intent. This skill
turns that naming into the invocation: find the skill's file, render it the way invocation
would, and run it.

The user chooses the skill. Run the one they named, in this conversation or in the Brief you
were handed, and leave every other skill alone.

When the named skill is in your skill list, invoke it through the Skill tool instead: that path
renders everything below for you.

## Procedure

1. **Find.** List every skill under the [skill roots](#skill-roots) and match the user's
   naming against them: first the frontmatter `name` or the file's folder (or file) name, with
   or without a `plugin:` prefix; then the `description`, for a skill named by what it does.
   Done when exactly one skill matches.
   - Several match: ask the user to pick, one line per candidate with its name, path and
     description.
   - None match: tell the user which roots you searched. A skill installed only on another
     machine is not reachable from here.

2. **Render.** Read the whole file and build the text invocation would have sent. The
   **arguments** are what the user would have typed after the slash command ("use the tdd
   skill on the parser" gives `the parser`).
   - Substitute every placeholder: `$ARGUMENTS` (all arguments), `$ARGUMENTS[N]` and `$N`
     (0-based positions), `$<name>` (positions named by the `arguments` frontmatter list),
     `${CLAUDE_SKILL_DIR}` (the skill's folder), `${CLAUDE_PLUGIN_ROOT}` (the plugin's
     installation folder, for plugin skills), `${CLAUDE_PROJECT_DIR}` (the project root). When
     the body has no `$ARGUMENTS` and arguments were given, append `ARGUMENTS: <arguments>`. An
     indexed placeholder with no argument, and a value you cannot know, stays as written.
     `\$` is a literal dollar sign.
   - Run each dynamic-context command, `` !`command` `` inline (at a line start or after
     whitespace) and each ` ```! ` fenced block, from the project root, and put its output in
     its place. A failing command aborts invocation: stop and tell the user which command
     failed.
   - Resolve relative links against the skill's folder.

   Done when the text you will follow has no placeholder left to fill and no command left to
   run.

3. **Run.** Tell the user in one line which file you are running. Then follow the rendered
   skill as if they had typed its slash command, to the skill's own completion criteria.
   - `context: fork`: hand the rendered skill to a subagent as its prompt, of the type named by
     `agent`, and relay its result.
   - `allowed-tools`, `model`, `effort` and `hooks` configure a real invocation only. Tools ask
     for permission as usual.

## Listing user-invoked skills

When the user asks which skills only they can invoke, search the same roots, keep the files
whose frontmatter sets `disable-model-invocation: true`, and list each on one line: its
name, path and description.

## Skill roots

A skill is a `SKILL.md` in its own folder, or a legacy command: a `<name>.md` in a `commands/`
folder, with the same frontmatter. A skill wins over a command of the same name.

- **Project**: `.claude/skills/` and `.claude/commands/` at the project root.
- **Personal**: `~/.claude/skills/` and `~/.claude/commands/`.
- **Plugins**: `~/.claude/plugins/`, and `$CLAUDE_CODE_PLUGIN_CACHE_DIR` when it is set. Copies
  of one plugin's skill (several versions, a marketplace clone) are one skill: read the copy in
  the newest version folder.

A skill can sit in nested folders below its root. To list them all, from the project root:

```bash
find .claude ~/.claude/skills ~/.claude/commands ~/.claude/plugins \
  ${CLAUDE_CODE_PLUGIN_CACHE_DIR:+"$CLAUDE_CODE_PLUGIN_CACHE_DIR"} \
  \( -name SKILL.md -o -path '*/commands/*.md' \) 2>/dev/null
```
