## Scratchpad

**Option 1: Implement `pytest-asyncio` and `pytest-cov` integration.**
*   **Concept:** Standardize the test suite by migrating to `asyncio_mode = auto` and integrating `pytest-cov` with `term-missing` reporting.
*   **Critique:** High feasibility. It directly addresses the "Technical Summary" learned this cycle. It improves observability of untested code paths.
*   **Trade-off:** Requires modifying `pytest.ini` and potentially refactoring existing async tests that rely on manual event loop management.
*   **Long-term:** Increases maintainability by reducing boilerplate and providing actionable coverage data.

**Option 2: Implement a "Semantic Cache" validation layer.**
*   **Concept:** Add a checksum-based validation to `bag/semantic_cache.py` to ensure that cached responses haven't been invalidated by underlying schema changes in `sam.py`.
*   **Critique:** Higher complexity. Requires tracking dependencies between cache keys and code versions.
*   **Trade-off:** Prevents "stale intelligence" but adds overhead to the `ask_gemini` flow.
*   **Long-term:** Increases reliability of agentic reasoning, but might be premature optimization compared to stabilizing the test suite.

**Decision:** Option 1 is the superior choice for this cycle. It aligns with the "Technical Summary" and provides the necessary foundation for future, more complex refactors.

---

## Idea: Standardizing Test Infrastructure and Coverage
Implement a robust `pytest` configuration and migrate legacy mock patterns to `pytest-mock` fixtures.

## Why
The current test suite lacks granular coverage reporting and relies on manual mock cleanup, which is prone to leakage. By standardizing on `pytest-asyncio` and `pytest-cov`, I gain immediate visibility into untested edge cases and ensure that my self-modification cycles are verified against a stable, modern harness.

## Implementation Steps
1.  **Configure `pytest.ini`:** Add `asyncio_mode = auto` and `addopts = --cov=. --cov-report=term-missing`.
2.  **Refactor Mocks:** Audit `bag/tests.py` to replace `unittest.mock.patch` with the `mocker` fixture.
3.  **Integrate `conftest.py`:** Move shared async fixtures into `conftest.py` to ensure clean, function-scoped event loops.
4.  **Verification:** Run `pytest` and analyze the `term-missing` output to identify the first high-priority module for unit test expansion.

## Risk
**Failure Mode:** `pytest-asyncio` might conflict with existing custom event loop fixtures in `bag/tests.py`, causing tests to hang or fail during initialization.
**Mitigation:** Perform a dry-run with `pytest -v` before committing the `pytest.ini` changes. If conflicts arise, I will isolate the event loop configuration to specific test classes rather than global `auto` mode.

**Confidence Score:** 9/10