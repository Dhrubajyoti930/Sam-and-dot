## Scratchpad

**Option 1: Implement `TestDatabaseProvider` (High Priority)**
*   **Concept:** Create a centralized utility to manage `:memory:` SQLite connections, ensuring lifecycle hooks (setup/teardown) are enforced.
*   **Critique:** This directly addresses the "connection leak" risk identified in my self-correction. It aligns with the goal of improving test reliability.
*   **Trade-offs:** Requires refactoring existing test suites to use the provider.
*   **Feasibility:** High. It is a contained, surgical change.

**Option 2: Integrate `Ragas` for Evaluation-Driven Development (Phase V)**
*   **Concept:** Introduce a basic `Ragas` pipeline to score the outputs of my `ask_gemini` calls against a small set of ground-truth examples.
*   **Critique:** While valuable, this is a significant shift in infrastructure. It might be premature before stabilizing the testing foundation.
*   **Trade-offs:** High complexity, potential for "vibe-based" evaluation if not carefully calibrated.
*   **Feasibility:** Moderate.

**Decision:** Option 1 is the most disciplined choice. It builds on the "Skill learned this cycle" and directly addresses the technical debt of test isolation.

---

## Idea
**Implementation of `TestDatabaseProvider` for Isolated SQLite Testing**

## Why
My current testing architecture lacks a standardized, safe way to handle in-memory database lifecycles. By centralizing this in a `TestDatabaseProvider`, I eliminate the risk of connection leaks, ensure schema consistency across tests, and provide a clean, repeatable environment that adheres to the "minimal footprint" principle.

## Implementation Steps
1.  **Create `bag/test_utils.py`:** Define a `TestDatabaseProvider` class using a context manager pattern (`__enter__`, `__exit__`) to ensure connections are closed.
2.  **Schema Injection:** Add a method to the provider that accepts a schema definition and applies it upon initialization.
3.  **Refactor `bag/tests.py`:** Update existing tests to instantiate the provider, replacing manual `sqlite3.connect(':memory:')` calls.
4.  **Enforce Cleanup:** Add a `__del__` or explicit `close()` hook to the provider to guarantee memory release.

## Risk
**Failure Mode:** The `shared cache` mode might cause race conditions if I attempt to run tests in parallel before the architecture is ready for concurrency.
**Mitigation:** I will default to private, non-shared memory connections for now, explicitly documenting that shared cache is an "opt-in" feature for specific multi-threaded test cases.

**Confidence Score:** 9/10