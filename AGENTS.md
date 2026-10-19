# Agent instructions

This repository is the DevFlow plugin.

- Coordinator: [`agents/devflow.md`](agents/devflow.md)
- Skills: [`skills/`](skills/), one folder per skill, each with a `SKILL.md`

## Structure of the Coordinator

The agent definition has three layers:

- **Philosophy** — why: the values.
- **Theory** — what: the concepts.
- **Practice** — how: the mechanics.

Philosophy informs Theory. Theory informs Practice. Edits should land in the layer they belong
to.

## Writing skills

Skills follow the [Agent Skills specification](https://agentskills.io/specification) and work
in any agent harness. Write each step in terms of what the agent does, and leave a harness's
mechanics (its tools, frontmatter fields, folders) to that harness's documentation, which stays
current as the harness changes.

## READMEs

A README embeds content from other files between `<!-- include: ... -->` and `<!-- /include -->`
markers. After editing a file that a README includes, run `node scripts/sync-readme.mjs`; CI
fails when a README is out of date.

## Commits and releases

Pull requests are squash-merged, so a pull request's title becomes its commit on main. Titles
follow [Conventional Commits](https://www.conventionalcommits.org), checked in CI against
[`commitlint.config.mjs`](commitlint.config.mjs), which lists the types and scopes. A change to
what the plugin ships (`agents/`, `skills/`, `references/`, the manifests) is a `feat` or a `fix`,
because users run that text.

Don't bump versions by hand. release-please keeps a release pull request open that bumps the
version in both manifests and updates `CHANGELOG.md`; merging it publishes the release.
