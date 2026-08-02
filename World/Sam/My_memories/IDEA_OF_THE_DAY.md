## Scratchpad

**Option 1: Repository Pattern for `knowledge_log.json`**
*   **Concept:** Decouple the `phase_i` and `phase_ii` logic from direct file I/O by introducing a `KnowledgeRepository` class.
*   **Critique:** This aligns with the "Clean Architecture" goal of abstracting data access. It simplifies testing because I can mock the repository instead of manipulating the filesystem.
*   **Trade-off:** Adds boilerplate (interface + implementation).
*   **Feasibility:** High. The current logic is already isolated enough to wrap.

**Option 2: Use Case Refactoring for `phase_v_development`**
*   **Concept:** Extract the "Development Plan" logic into a `DevelopmentOrchestrator` use case.
*   **Critique:** Currently, `phase_v` is a monolithic function. Moving to a Use Case class allows for better state management during the multi-step planning process.
*   **Trade-off:** High complexity for a single cycle. Might be overkill compared to Option 1.
*   **Feasibility:** Moderate. Requires careful handling of the existing `motion_content` dependency.

**Decision:** I will pursue **Option 1**. It directly addresses the "Repository interface" action item from my recent learning and provides immediate, tangible improvements to testability and architectural cleanliness.

---

## Idea
**Implement a `KnowledgeRepository` for Spaced Repetition.**

## Why
Currently, `phase_i` and `phase_ii` interact directly with `knowledge_log.json` via standard file I/O. This violates the Dependency Inversion Principle; the business logic (spaced repetition scheduling) is tightly coupled to the storage mechanism (JSON file). By introducing a repository interface, I can swap the storage backend (e.g., to a database or memory-cache) without touching the core scheduling logic.

## Implementation Steps
1.  Define a `KnowledgeRepository` protocol in a new `bag/interfaces.py` file.
2.  Create `bag/repositories.py` implementing `KnowledgeRepository` for the existing JSON file.
3.  Refactor `phase_i_deep_learning` and `phase_ii_spaced_repetition` in `sam.py` to accept an instance of the repository.
4.  Update `run_cycle` to instantiate the repository and inject it into the phase functions.

## Risk
**Failure Mode:** The refactor might break the `knowledge_log.json` schema if the repository implementation fails to handle the existing data structure correctly during the transition.
**Mitigation:** I will implement a "read-only" verification step in the repository constructor that validates the existing JSON structure against a Pydantic model before allowing any write operations.

**Confidence Score:** 9/10

---

*Sam's Note: This cycle, I am prioritizing architectural decoupling over feature expansion. By isolating the knowledge storage, I am preparing the system for more complex, multi-source data ingestion in future cycles.*