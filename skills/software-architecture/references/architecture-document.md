# Architecture document

An architecture document captures what the code cannot easily show: the system's structure at
a level above any single codebase. Document the Context and Containers. Components are
inferable from code; documenting them adds maintenance burden for limited value.

The document is the normalized source of truth: state each fact once, in one place, and refer
to other facts by name. Whatever can be derived from it, such as the visualization, stays out
of it.

Leave scenarios out of the document: architecture is structure, scenarios are behavior and
change with every feature. Use them to test the picture instead. A scenario that cannot be traced
through the containers and the relevant lenses means the picture is incomplete.

## Evidence

Write down what actually runs, not what the code implies. Mark each element and connection
**verified** when backed by a source you read that defines or performs it (deployment or
infrastructure config, or the code making the call), and **inferred** when deduced from
indirect signals (names, comments, conventions) or from a part whose defining source you
could not see.

## Template

Angle brackets are placeholders. Every claim gets its own `Evidence:` line, and every
`<evidence>` is either ``verified: `<path>` ``, the source you read that defines or performs
it, or `inferred: <why>`, the indirect signal it rests on.

```markdown
# Architecture

## Context

<What the system does, in one or two sentences: the premise, not the feature list.>

### Actors
- **<actor>**: <role>
  - Goal: <what they come to the system for>
  - Evidence: <evidence>

### External systems
- **<system>**
  - Provides: <the capability the system relies on it for>
  - Evidence: <evidence>

### Environments
- **<environment>**: <what it is for>
  - Evidence: <evidence>
  - Hosting:
    - <host>
    - <host>

## Containers

### <container>
- Responsibility: <what it owns>
- Evidence: <evidence>
- Technology:
  - <environments>: <stack> on <host>
    - Evidence: <evidence>

## Communication
- **<initiator> → <target>**: <protocol>
  - Flows:
    - → <what moves with the call>
    - ← <what comes back>
  - Evidence: <evidence>
```

A Technology entry's host must be listed under Hosting in every environment the entry names,
and its evidence must cover every environment it names.

Communication lists every connection that involves a container: between containers, and
between a container and an actor or external system. A connection is one initiator, one
target, and one protocol. Its flows are the data it carries: `→` moves with the initiator's
call, `←` comes back to it. List each connection once, grouped by its initiator: actors
first, then external systems, then containers, each in the order the document defines them.
Within one initiator, order the targets the same way.

See [architecture-document-example.md](architecture-document-example.md) for a filled-in
example.
