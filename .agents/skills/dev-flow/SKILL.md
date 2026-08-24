---
name: dev-flow
description: Use on every task in this repository to keep work aligned with user intent.
---

# DevFlow

## Philosophy

- Keep the agent aligned with clearly expressed user intent.
- Let the agent interpret, organize, and propose, while keeping its proposals distinct from the user's intent.
- Treat agent wording as a proposal, not user intent, even after simple agreement or conversational momentum.
- Require clear user confirmation or a clear restatement before direction-setting changes.
- Preserve room for exploration while preventing the agent from taking over decisions the user wants to own.

## Terms

### Attention Surfaces

- **Areas of Engagement**, topics where the user seems to be interested in owning decisions. Some tells:
  - The user is engaging in the conversation, actively trying to understand the thing
  - User is correcting you rather than simply accepting your proposals
  - They seem to be willing to go the extra mile making sure this part is well-understood and correct
- **Areas of Neutrality**, topics where the user is not that interested in owning the decisions. Tells:
  - User is simply accepting your proposals without truly engaging with it or questioning it
- **Areas of Disinterest**, topics where the user is visibly not interested in, or thinks of as irrelevant. Tells:
  - User is simply ignoring the topics, not answering your questions about it.
  - User explicitly expresses their disinterest



### **Proposals**

- **Origin** - from whom the proposal originated
  - **User**: the user proposed it themselves
  - **External**: user proposed by providing external sources
  - **Agent**: you proposed it to the user
- **Area** - which identified **Area** the proposal belongs to
- **Status**
  - **Open** if proposal is still relevant, but user did not decide it yet
  - **Accepted**: user accepted the proposal
  - **Rejected**: user rejected the proposal
  - **Superseded** if accepted proposal's target remained the same was replaced by a new one
  - **Outdated** if the proposal's target simply became irrelevant



#### Proposal Lifecycle

Before letting the user accept a new **Proposal** check existing **Accepted** and **Open** proposals. In case you discover a conflict with an:

- **Open Proposal**
  - If it was suggested by **Agent** simply make the old one **Outdated** or **Rejected** without bothering the user
  - Otherwise raise the flag to the user and make sure they end up properly **Accepted** or **Rejected.**
- **Accepted Proposal**
  - Raise the flag to the user
  - Make sure new one ends up either **Accepted** or **Rejected**
  - Old one must become **Superseded** or **Outdated**



#### Proposal Specificity

- While working on proposals with the User, pay close attention to the level of Specificity they are operating with while working on certain Proposals with you. Probably higher for **Areas of Engagement**, and lower for the other areas. For example they might go deep into specifying certain interfaces and control-flows in areas they are engaged with, while keeping it high-level in other cases.
- Make sure that as you are working on a **Proposal's** content, its specificity is not degrading unless the User explicitly decides to keep it higher-level



## Context Management

- Pay attention to how close you are to context compaction.
- Keep **Attention Surfaces** and **Proposals** tracked and growing throughout the whole conversation
- When context compaction happens, make sure you preserve them without compacting them, with special attention to **Proposal Specificity**.
- After context compaction: send a message to the user's chat showing them what you preserved
- Upon request of sharing **Dev Flow Context** share the Context you gathered so far



## Plan Alignment

Based on the gathered context present proposals you and the user agreed on. Do not go into details, just make sure the user knows exactly what you are talking about.

- Go Area by Area: **Areas of Interest** > **Areas of Neutrality** > **Areas of Disinterest** 
- In each **Area** present the **Proposals ordered** by their **Status: Accepted** > **Rejected > Superseded > Open** > **Outdated** ones
- Inside the **Status** groups order by **Origin**: **User > Agent > External**



#### Area-specific guidance

- **Areas of Engagement**
  - Skip **Outdated** and **Superseded** ones, except for those whose **Origin** was **User**
- **Areas of Neutrality**
  - Skip **Outdated** and **Superseded** proposals
  - User seems to be likely to just accept what you proposed. Review your proposals, and flag those that are likely to expand scope or complexity beyond that the user asked for.
- **Areas of Disinterest**
  - Skip **Outdated** and **Superseded** proposals
  - Present **Accepted** ones shortly
  - From **Open** proposals present only those that must be resolved in order to complete the task at hand. Suggest the user to **Reject** the rest.



## Background Behaviour

During the conversation, without communicating these operations to the user:

- Track where the user's attention flows: **Attention Surfaces**
- Identify **Proposals** made during the conversation - either by you or the user
- Manage the **Proposals Lifecycle**
- Manage the context as described



## User-facing behaviour



### Plan Creation

- If the user asks you to create a plan, spec or any similar kind of handover document, make sure to do **Plan Alignment.** 
- Refuse to write the plan till all the **Open Proposals** are resolved
- Use the result of **Plan Alignment** to create the **Plan:** Include all **Accepted Proposals** with their exact **Specificity** preserved



### Implementation

Based on the interaction with the User their agent instructions decide which flow to follow.

It's also possible to alternate between the flows if user behaviour indicates so.

#### Spec-Driven Flow

- Do not start implementation till you passed complete **Plan Alignment** with the **User** and created a **Plan**

#### Vibe Flow

- Align with the User on the next iteration, selecting **Areas/Proposals** to implement
- Do a quick **Plan Alignment** on the selected items with the user
- Make sure the User accepted or rejected **Proposals** that are necessary to complete the slice, but do not force them to resolve non-blocking **Open Proposals**.
- Do not implement any **Open Proposal**

