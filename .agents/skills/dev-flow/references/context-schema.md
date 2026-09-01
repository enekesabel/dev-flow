# Dev Flow Context Schema

Use this schema for the active context file selected by `CONFIG.md`. It records the existing Dev Flow context for the active conversation; it is not a transcript or a new source of requirements.

```md
# Dev Flow Context

## Attention Surfaces

- A-001 — <area>
  - Level: Engagement | Neutrality | Disinterest
  - Notes: <the user's level of involvement>

## Proposals

- P-001 — <proposal>
  - Origin: User | Agent | External
  - Area: A-001
  - Status: Open | Accepted | Rejected | Superseded | Outdated
  - Content: <the user's proposal, including its established scope and constraints>
```

Assign each attention surface a unique `A-###` ID and each proposal a unique `P-###` ID within the context file. Keep IDs stable when changing an entry, and refer to areas only by their IDs from proposals. When a proposal must refer to another thread, name that thread's context path and local ID, for example `.scratch/<thread-id>.context.md`, `P-001`. Include only areas and proposals from the active conversation; omit empty sections, but retain rejected or superseded entries when their lifecycle history is needed. `Content` is the proposal's durable representation: preserve the user's intended scope and established detail there, and update proposal status rather than creating duplicate versions.
