## Scratchpad

**Option 1: Implement a "Test Double Registry" for the Workshop Bench.**
*   **Concept:** Create a centralized registry in `bag/` that provides pre-configured fakes (e.g., `FakeRepository`, `FakeEventBus`) for common dependencies.
*   **Critique:** High maintainability. It standardizes how we isolate components. However, it risks becoming a "god object" if not scoped correctly.
*   **Feasibility:** High. It aligns with the "Test Doubles" skill learned this cycle.

**Option 2: Transition `_parse_gemini_json` to a Pydantic-first validation layer.**
*   **Concept:** Replace the manual regex-based extraction with a more robust `Instructor`-style approach using Pydantic models for all LLM interactions.
*   **Critique:** This significantly improves reliability and type safety. However, it introduces a dependency on `pydantic` (if not already strictly enforced) and requires refactoring every `ask_gemini` call site.
*   **Feasibility:** Medium. It is a large refactor that might trigger the "minimal footprint" constraint.

**Selection:** Option 1 is more aligned with the "Minimal footprint, maximum leverage" trait. It provides immediate value to the test suite without requiring a massive architectural overhaul.

---

## Idea: Test Double Registry for Workshop Bench

Implement a `bag/test_doubles.py` module that provides a factory-based registry for common fakes, enabling consistent state-based verification across the `workshop_bench/` suite.

## Why
Currently, test doubles are likely implemented ad-hoc within individual test files, leading to duplication and inconsistent behavior. A centralized registry allows for "Fakes" that are reusable, type-hinted, and easily injected, reducing the brittleness of our current mock-heavy tests.

## Implementation Steps
1.  **Create `bag/test_doubles.py`**: Define a base `Fake` class and specific implementations (e.g., `InMemoryRepository`).
2.  **Expose a Factory**: Provide a simple `get_fake(name: str)` interface to retrieve these objects.
3.  **Refactor**: Update one existing test file in `workshop_bench/` to use the `InMemoryRepository` instead of `unittest.mock.MagicMock`.
4.  **Document**: Add a brief entry to the project documentation regarding the use of this registry.

## Risk
**Failure Mode:** The registry becomes a bottleneck or a source of "stale state" if fakes are not properly reset between tests.
**Mitigation:** Implement a `reset()` method on the base `Fake` class and enforce a `teardown` fixture in the test suite that calls `registry.clear_all()`.

**Confidence Score: 9/10**