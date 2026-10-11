---
name: system-architecture
description: Use when you are the DevFlow Coordinator and the conversation turns to a software system's architecture: identifying it, discussing it, or documenting it (what its boundary is, what runs inside it, where it runs, how its parts communicate), or when writing, reviewing, or updating an ARCHITECTURE.md or an architecture diagram. Otherwise use only when explicitly told to.
---

# System Architecture

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

## The boundary

Identify the boundary first, then what crosses it.

- **Actors** — who or what comes to the system with a goal: users, operators, other software
  that uses it.
- **External systems** — other software systems outside the boundary that provide a capability
  the system relies on; the system's team does not own or have responsibility for them (C4).

Ownership decides where something that runs belongs, not where its code lives or how it is
packaged: what the system's team builds or runs is inside the boundary, as a container or as
part of one; what another party builds and runs is an external system.

## Containers

A container is a runtime unit inside the boundary: something that needs to be running for the
system to work (C4). Containers are the system's own: its team builds them or is responsible
for running them. Name each by its role; what it is built with and where it runs belong to its
technology, per environment.

For example:
- an application or service
- a worker or scheduled job
- a data store
- a queue

A single-page app is its own container even when the backend serves it: it runs separately
from the backend. A library compiled into an application is part of that container. Code that
another party builds and runs belongs to that party's external system, even when it runs
inside one of the system's containers, such as an embedded third-party widget.

## Documenting and visualizing

- To write an architecture document, follow [references/architecture-document.md](references/architecture-document.md).
- To visualize the architecture, follow [references/architecture-visualization.md](references/architecture-visualization.md).


## Before you finish

Check the picture against itself. A failed check is a finding to raise with the user, with
what you found and where, not something to resolve on your own.

- Every actor, external system and container takes part in at least one connection.
- Every connection has an actor, external system or container at each end.
- Every element and connection carries evidence, verified or inferred.
- Every environment lists every container and every external system.
