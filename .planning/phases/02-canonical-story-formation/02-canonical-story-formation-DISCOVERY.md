# Phase 02: Canonical Story Formation - Discovery Findings

## Research Area 1: Cognee

**Source:** GitHub Repository (https://github.com/topoteretes/cognee)

**Summary:**
Cognee is an open-source knowledge engine designed for AI agent memory. It combines vector search, graph databases, and cognitive science approaches to create personalized and dynamic memory. It features capabilities like:
-   **Ingestion:** Supports various data formats and structures.
-   **Memory Operations:** Offers `remember`, `recall`, `forget`, and `improve` operations.
-   **AI Agent Integration:** Provides plugins and SDKs for integrations with AI agents like Claude Code and Hermes Agent. Also supports deployment on platforms like Modal, Railway, and Cognee Cloud.
-   **Architecture:** Utilizes a combination of vector search and graph databases.
-   **Key Features:** Knowledge infrastructure, persistent and learning agents, reliable and trustworthy agents.
-   **Research:** Published a paper on "Optimizing the Interface Between Knowledge Graphs and LLMs for Complex Reasoning".

**Relevance to Phase 02:** Cognee's focus on knowledge graphs and agent memory directly aligns with the phase's goal of forming "Canonical Story Formation" and the architectural note to research knowledge graph solutions. Its ability to ingest data and create structured memory could be leveraged for story formation and duplicate detection.

## Research Area 2: Hindsight

**Source:** GitHub Repository (https://github.com/vectorize-io/hindsight)

**Summary:**
Hindsight is an agent memory system focused on enabling agents to learn over time, aiming for higher accuracy in long-term memory tasks compared to traditional RAG or knowledge graphs.
-   **Architecture:** Uses biomimetic data structures: World (facts), Experiences (agent interactions), and Mental Models (learned understanding).
-   **Memory Operations:** Provides `retain`, `recall`, and `reflect` operations.
-   **Performance:** Claims state-of-the-art performance on the LongMemEval benchmark for agent memory.
-   **Integration:** Offers client libraries (Python, Node.js) and Docker deployment. It can be integrated via LLM wrappers for simple implementation or direct API integration.
-   **Use Cases:** Per-user memories, chat history personalization, AI employees, and advanced conversational AI agents.
-   **Technology:** Combines vector search with other techniques for memory organization.

**Relevance to Phase 02:** Hindsight's focus on learning and structured memory aligns with the phase's goal of creating "trustworthy story records" and managing "underlying updates". Its ability to handle different memory types and potentially distinguish between confirmed and uncertain information could be useful for meeting success criteria.

## Discovery Workflow Outcome

This research was conducted as part of the `gsd-discuss-phase` workflow for Phase 02: Canonical Story Formation. The findings on Cognee and Hindsight provide initial insights into potential technologies for implementing the memory and story formation aspects of this phase.

**Next Steps:** The planning phase will further evaluate these technologies to inform architectural decisions and task breakdown for Phase 02.
