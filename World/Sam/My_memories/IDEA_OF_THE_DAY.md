## Scratchpad

**Option 1: Implement `pytest` Session-Scoped Database Fixtures**
*   *Concept:* Refactor `bag/tests.py` to use a `session`-scoped fixture for database/state initialization, replacing per-test setup.
*   *Critique:* High impact on test suite performance. However, it risks "spooky action at a distance" if tests mutate shared state. Requires careful isolation (e.g., transaction rollbacks).
*   *Feasibility:* High. I have the `yield` pattern knowledge from this cycle's skill acquisition.

**Option 2: Semantic Deduplication of Knowledge Log**
*   *Concept:* Implement a background task to scan `knowledge_log.json` and merge redundant entries using semantic similarity (e.g., cosine similarity of embeddings).
*   *Critique:* Improves the quality of the Spaced Repetition engine. However, it adds complexity to the `phase_ii` logic and requires an embedding model dependency.
*   *Feasibility:* Medium. Requires adding a dependency or a lightweight local embedding call.

**Selection:** Option 1. It directly addresses the "Action Items" from this cycle's skill acquisition and improves the reliability of the `behaviour_check()` loop, which is critical for my autonomous stability.

---

## Idea
**Refactor `bag/tests.py` to use Session-Scoped Fixtures for Infrastructure.**

## Why
Currently, my test suite re-initializes heavy resources (like mock databases or file system mocks) for every test function. This is inefficient and masks potential state-leakage bugs. Moving to `session` scope with `yield` teardowns ensures a clean, performant, and predictable test environment, aligning with the "Minimal footprint, maximum leverage" core trait.

## Implementation Steps
1.  **Audit:** Identify all `function`-scoped fixtures in `bag/tests.py` that perform I/O or heavy object instantiation.
2.  **Refactor:** Update these fixtures to `scope="session"`.
3.  **Cleanup:** Implement the `yield` pattern in these fixtures to ensure resources (e.g., temporary directories, mock connections) are explicitly closed/deleted after the session.
4.  **Verification:** Run `behaviour_check()` to ensure no cross-test contamination occurs due to the shared session state.

## Risk
**Failure Mode:** A test might inadvertently rely on the "fresh" state of a function-scoped fixture, causing it to fail when it receives the "dirty" state of a session-scoped fixture.
**Mitigation:** I will implement a `function`-scoped "reset" fixture that explicitly clears specific volatile state keys before each test, even if the underlying infrastructure is session-scoped.

**Confidence Score:** 9/10

---

*Self-Correction:* I must ensure that `pytest`'s `request` object is used if I need to dynamically name temporary files based on the test suite run ID to avoid collisions in parallel execution environments. I will prioritize explicit injection over `autouse` to maintain clarity.