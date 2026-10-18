---
name: use-skill
description: Use when the user tells you to use a skill, by its name, its author or what it does, that is not in your list of skills, before you try to invoke it. Also when a listed skill shares a word with the one they named but their wording, such as an author, points to another. Also when the user asks which skills only they can invoke.
---

# Use Skill

A **user-invoked** skill is one your harness hides from you and starts only when a person
invokes it by hand, usually with a slash command. A person telling you to use it in plain words
carries the same intent. This skill turns that naming into the invocation: find the skill's
file, prepare it the way invocation would, and follow it.

Run the skill the user named, and only that one. When it is in your list of skills, invoke it
yourself instead: your harness then prepares it for you. When your harness refuses it, stop and
tell the user it is theirs to invoke, with the command to type.

## Procedure

1. **Find.** A skill follows the
   [Agent Skills specification](https://agentskills.io/specification): a folder holding a
   `SKILL.md` whose frontmatter `name` matches the folder's name. Search the folders your
   harness loads skills from: by convention `.agents/skills/` and `.<harness>/skills/`, in the
   project and in the home directory, plus installed plugins'. Match the user's whole naming,
   including an author or source they give, against what you find: first the `name` and the
   skill's path; then the `description`, for a skill named by what it does. Copies of one
   skill (several plugin versions, a marketplace clone) count as one: read the newest. When
   the project and the home directory both have a skill with that name, the project's wins.
   Done when exactly one skill matches.
   - Several different skills match: ask the user to pick, one line per candidate with its
     name, path and description.
   - None match: tell the user where you searched. A skill installed only on another machine is
     not reachable from here.

   When you don't know your harness's skill folders, use your file-search tool to find
   `SKILL.md` files under the project and the home directory.

2. **Prepare.** Read the whole file, and resolve its relative paths against the skill's
   folder, as the specification does. Beyond the specification, a harness can transform a
   skill when it invokes it: substitute the arguments into placeholders, insert the output of
   shell commands. Do each of those yourself, the way your harness would; its documentation is
   the source for syntax you don't recognize. The **arguments** are what the user would have
   typed after the slash command ("use the tdd skill on the parser" gives `the parser`). Done
   when nothing is left in the text that invocation would have replaced.

3. **Run.** Before anything else, tell the user in one line which skill you are running and
   its path. Then follow the prepared skill as if they had invoked it, to the skill's own
   completion criteria. When the skill declares that it runs in a separate context, hand it to
   a subagent as its prompt and relay the result.

## Listing user-invoked skills

When the user asks which skills only they can invoke, search the same folders, keep the skills
your harness marks as user-invoked, and list each on one line: its name, path and description.
