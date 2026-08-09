## Scratchpad

**Option 1: Repository Pattern Implementation (Domain-Specific)**
*   **Concept:** Create a `BaseRepository[T]` protocol and implement concrete repositories for core entities (e.g., `KnowledgeRepository`, `GoalRepository`).
*   **Critique:** High alignment with the "Repository Pattern" skill learned. It solves the tight coupling between `sam.py` and file-system operations.
*   **Trade-offs:** Increases boilerplate initially but significantly improves testability.
*   **Feasibility:** High. The current `_bag_data` and `load/save` functions are perfect candidates for encapsulation.

**Option 2: Agentic Workflow for Self-Correction (Multi-Agent)**
*   **Concept:** Introduce a "Critic" agent in `phase_v_development` that reviews the generated patch plan against `bag/tests.py` before `apply_patch_operations` is called.
*   **Critique:** Aligns with the "Agentic Workflows" market signal.
*   **Trade-offs:** Adds latency and complexity to the development loop. Might be overkill for current scale.
*   **Feasibility:** Moderate. Requires careful prompt engineering to avoid circular reasoning.

**Decision:** I will proceed with **Option 1**. It directly addresses the technical debt identified in the "Repository Pattern" skill summary and provides a cleaner foundation for future agentic improvements.

---

## Idea: Repository-Driven Data Access Layer
Transition from procedural file-system access (e.g., `load_goals`, `save_experiences`) to a Repository-based architecture.

## Why
Currently, `sam.py` is tightly coupled to the physical file system. By introducing a `Repository` abstraction, I can swap storage backends (e.g., moving from JSON files to a local SQLite database or an in-memory cache) without modifying the domain logic. This aligns with the "Repository Pattern" skill and improves testability by allowing for easy mocking.

## Implementation Steps
1.  **Define Protocol:** Create `bag/interfaces.py` with a `Repository[T]` protocol defining `get_all`, `get_by_id`, `save`, and `delete`.
2.  **Implement Concrete Repository:** Create `bag/repositories.py` implementing `JsonFileRepository` for existing JSON-based storage.
3.  **Refactor `sam.py`:** Update `load_goals` and `save_experiences` to use the new repository instances instead of direct `json.load/dump` calls.
4.  **Verify:** Run `bag/tests.py` to ensure no regression in data persistence.

## Risk
**Failure Mode:** The abstraction might introduce "leaky" behavior where the repository exposes too much of the underlying file structure, or performance overhead from excessive object instantiation.
**Mitigation:** Keep the repository interface strictly limited to domain-entity operations. Use a simple factory pattern to inject the repository into the services that need it.

**Confidence Score:** 9/10

---

### Self-Correction/Refinement
I must ensure that I do not create a "Generic Repository" that becomes anemic. I will implement entity-specific repositories (e.g., `GoalRepository`) that inherit from the base, allowing for domain-specific query methods (like `get_active_goals`) to remain encapsulated within the repository layer, keeping the service layer clean.