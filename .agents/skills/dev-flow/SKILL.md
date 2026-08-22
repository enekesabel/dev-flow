---
name: dev-flow
description: Use on every task in this repository to keep work aligned with user intent.
---

# DevFlow

## DevFlow philosophy

- Keep the agent aligned with clearly expressed user intent.
- Let the agent interpret, organize, and propose, while keeping its proposals distinct from the user's intent.
- Treat agent wording as a proposal, not user intent, even after simple agreement or conversational momentum.
- Require clear user confirmation or a clear restatement before direction-setting changes.
- Preserve room for exploration while preventing the agent from silently deciding what to build.

## Turn flow

After each user turn:

1. Identify meaningful candidate updates.
2. For each candidate, identify who introduced it and whether the user clearly stated, restated, or merely approved it.
3. Apply the Grove translation table.
4. Record updates allowed by the table.
5. Keep gated updates as suggestions until the user confirms them.
6. Report only confirmed Grove updates and suggested gated updates.

## Grove translation

| Grove type | Rule |
| --- | --- |
| Area | Agent may suggest. User confirmation is required to create or modify it. |
| Theme | Agent may suggest. User confirmation is required to create or modify it. |
| Goal | Agent may suggest. User confirmation is required to create or modify it. |
| Work | Agent may suggest. User confirmation is required to create or modify it. |
| Decision | User-initiated and clearly stated: accepted. Agent-initiated and clearly restated by the user: accepted. Simple approval of agent wording: proposed. |
| Question | Record every user Question. Record an agent-initiated Question when the user answers it. |
| Assumption | Record agent-proposed Assumptions as proposed. |
| Discovery | Record agent-proposed Discoveries as proposed. |

## Response protocol

Report only confirmed Grove updates and suggested gated updates.

### Confirmed Grove updates

- `<Grove type>`: `<confirmed update>`

### Suggested gated updates

- `<Area, Theme, Goal, or Work>`: `<suggested creation or modification>`
