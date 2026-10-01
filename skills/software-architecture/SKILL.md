---
name: software-architecture
description: Use when you are the DevFlow Coordinator and the conversation turns to a software system's architecture: identifying it, discussing it, or documenting it (what its boundary is, what runs inside it, where it runs, how its parts communicate), or when writing, reviewing, or updating an ARCHITECTURE.md or an architecture diagram. Otherwise use only when explicitly told to.
---

# Software Architecture

The concepts used here (Systems Thinking, Complexity and Abstraction) are defined in the [Coordinator's agent definition](../../agents/devflow.md).

## How to look at software systems

A software system has no single true picture. Two established frameworks capture this:

**Zoom levels** (C4 model, Simon Brown) control the scope of what you're looking at:

1. **Context** — the system from outside. Where does data enter and leave? Who are the
   actors beyond the boundary? What external systems does it talk to?
2. **Container** — inside the system. What are the separate runtime units? How do they
   communicate? Which ones handle data entering and leaving the boundary?
3. **Component** — inside one container. What are its building blocks? What does each one
   own? How do they depend on each other?
4. **Code** — inside one component. The actual files, classes, functions.

**Lenses** (4+1 Architectural Views, Kruchten 1995) control what aspect you're examining.
At any zoom level, these ask different questions:

- **Logical** — what does each part do? What are its responsibilities, interfaces,
  relationships?
- **Process** — what runs? How does data flow at runtime? What communicates with what?
  What happens concurrently?
- **Development** — where does the code live? How is it organized, built, packaged?
- **Physical** — where does each thing actually run? What infrastructure hosts it?

The same thing looks different through different lenses. A message broker is one component
through the Logical lens (an interface your code talks to), a separate container through the
Process lens (a runtime unit doing temporal decoupling), a library dependency through the
Development lens, and a managed service through the Physical lens. That is not a problem to
resolve — it is the reason multiple lenses exist. The right lens is the one that answers
the question you are asking.

## Writing an ARCHITECTURE.md

An architecture document captures what the code cannot easily show: the system's structure at
a level above any single codebase. Document the Context and Containers. Components are
inferable from code; documenting them adds maintenance burden for limited value.

Leave scenarios out of the document: architecture is structure, scenarios are behavior and
change with every feature. Use them to test the picture instead. A flow that cannot be traced
through the containers and the relevant lenses means the picture is incomplete.

### Context

Look at the system from outside. Apply systems thinking: identify the boundary first, then
what crosses it.

- **What the system does** — one or two sentences. The premise, not the feature list.
- **Actors** — who or what interacts with the system from outside. Users, operators,
  external services, scheduled jobs that trigger it.
- **Data entry points** — where data enters the system boundary. UI, public API, webhooks,
  file imports, message subscriptions.
- **Data exit points** — where data leaves. Responses, outbound API calls, notifications,
  exports, events published to external consumers.
- **External systems** — what the system depends on or feeds into beyond its boundary.

An external system is another software system outside the boundary: one the system's team
does not own or have responsibility for, that the system depends on or that depends on it
(C4).

### Containers

Look inside the system. Identify the separate runtime units and how they communicate.

- **Each container** — name it, state what it is responsible for, note its technology.
- **Communication** — how containers talk to each other. Synchronous (HTTP, gRPC) or
  asynchronous (message broker, event bus). Name the protocol, not just the arrow.
- **Boundary mapping** — which containers sit at the system boundary, handling data entry
  and exit points identified in Context.

Write down what actually runs, not what the code implies. Something is a container when
either criterion holds:

- **Separate deployment** — independently deployable. A Docker container, a Lambda function,
  a managed service, a widget with its own build pipeline.
- **Separate runtime boundary** — runs in a different process or environment, even if
  deployed together. A browser-side SPA served by the backend runs in the user's browser,
  not on the server. It is a container.

A library compiled into the application satisfies neither — it is not a container.

