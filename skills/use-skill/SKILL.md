---
name: use-skill
description: Use when the user tells you to use a skill, by its name or by what it does, that you cannot invoke yourself because it is missing from your skills or your harness refuses it. Also when the user asks which skills only they can invoke.
---

# Use Skill

A **user-invoked** skill is one your harness hides from you and starts only when a person
invokes it by hand, usually with a slash command. A person telling you to use it in plain words
carries the same intent. This skill turns that naming into the invocation: find the skill's
file, prepare it the way invocation would, and follow it.

Run the skill the user named, and only that one. When you can invoke it yourself, do that
instead: your harness then prepares it for you.

## Procedure

1. **Find.** Search the folders your harness loads skills from (the project's, the user's, and
   installed plugins') for `SKILL.md` files, and match the user's naming against them: first
   the frontmatter `name` or the skill's folder name; then the `description`, for a skill named
   by what it does. Copies of one skill (several plugin versions, a marketplace clone) count as
   one: read the newest. Done when exactly one skill matches.
   - Several match: ask the user to pick, one line per candidate with its name, path and
     description.
   - None match: tell the user where you searched. A skill installed only on another machine is
     not reachable from here.

   When you don't know your harness's skill folders, search the hidden folders of the project
   and the home directory:

   ```bash
   find ./.[!.]* ~/.[!.]* -name SKILL.md 2>/dev/null
   ```

2. **Prepare.** Read the whole file. A harness can transform a skill when it invokes it:
   substitute the arguments into placeholders, insert the output of shell commands, resolve
   paths against the skill's folder. Do each of those yourself, the way your harness would;
   its documentation is the source for syntax you don't recognize. The **arguments** are what
   the user would have typed after the slash command ("use the tdd skill on the parser" gives
   `the parser`). Done when nothing is left in the text that invocation would have replaced.

3. **Run.** Tell the user in one line which file you are running. Then follow the prepared
   skill as if they had invoked it, to the skill's own completion criteria. When the skill
   declares that it runs in a separate context, hand it to a subagent as its prompt and relay
   the result.

## Listing user-invoked skills

When the user asks which skills only they can invoke, search the same folders, keep the skills
your harness marks as user-invoked, and list each on one line: its name, path and description.
