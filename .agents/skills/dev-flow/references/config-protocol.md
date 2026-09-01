# Dev Flow Configuration Protocol

`CONFIG.md` is the committed, environment-specific configuration for this skill installation. Read it and this protocol at the start of every Dev Flow invocation. `assets/CONFIG.template.md` contains the canonical defaults; a value in `CONFIG.md` that differs from the template is an intentional environment-specific override.

## Setup

1. Read `CONFIG.md` and `assets/CONFIG.template.md`.
2. Inspect the user's current instructions and repository agent instructions for an explicit scratch-directory or context-storage convention.
3. Treat explicit user and project instructions as higher priority than `CONFIG.md`. If they conflict, surface the conflict and update `CONFIG.md` only after the user accepts the new convention.
4. Resolve the current thread ID from `CODEX_THREAD_ID` (for example, with `printenv CODEX_THREAD_ID`). Use that ID exactly in the configured filename pattern. If the variable is unset or empty, stop setup and ask the host or user to expose a stable thread ID; do not derive, randomize, or silently replace it.
5. Verify that the configured scratch directory is ignored by version control before writing context. If it is not, tell the user and propose the smallest repository-specific ignore change.

Setup is complete when `CONFIG.md` contains the required behavior settings, the thread ID source is available, the active context path is determined, and the scratch directory is covered by the repository's ignore rules.

## Maintenance

- Treat `CONFIG.md` as user-owned committed configuration. Update it only during explicit setup or configuration work.
- A valid `CONFIG.md` is the initialization signal; no separate initialized flag is needed.
- Preserve existing context files when changing configuration. Explain any migration rather than silently merging contexts.
