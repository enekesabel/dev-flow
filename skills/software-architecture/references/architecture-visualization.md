# Visualizing the architecture

Draw from the [architecture document](architecture-document.md), not from fresh exploration.
Use the environment's own visualization capability (canvas, artifact, or diagram skill).

- **One picture.** The containers sit inside the system boundary, with the Context's actors
  and external systems around it.
- **Edges reach the containers.** Edges from actors and external systems connect to the
  container they interact with, not to the system boundary.
- **Grouping follows the Physical lens:** group and color containers by the hosts of the
  environment shown. Let the viewer switch environments; show the development
  environment by default.
- **Distinct kinds:** actors, containers, and external systems look different from each other.
- **Labeled edges:** what flows and the protocol, pointing from the side that initiates.
- **Inferred versus verified:** shown differently, with a legend.
