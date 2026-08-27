## Scratchpad

**Option 1: Implement `pytest` Transactional Fixtures for `AsyncSession`**
*   **Concept:** Create a `conftest.py` in the test suite that manages `AsyncSession` via `pytest-asyncio`, using a `SAVEPOINT` pattern to ensure database isolation.
*   **Critique:** High impact on test reliability. It directly addresses the "Action Items" from the market scan.
*   **Trade-off:** Requires careful handling of the `event_loop` fixture to avoid `RuntimeError` when using `SQLAlchemy`'s `AsyncEngine`.
*   **Feasibility:** High. I have the technical summary from the market scan to guide the implementation.

**Option 2: Integrate `Testcontainers` for Integration Testing**
*   **Concept:** Replace `sqlite:///:memory:` with a real Postgres instance via `Testcontainers` for high-fidelity integration tests.
*   **Critique:** Provides the highest fidelity, but introduces a dependency on Docker/Podman in the environment.
*   **Trade-off:** Slower test execution compared to in-memory SQLite, but significantly reduces "it works in test but fails in prod" bugs.
*   **Feasibility:** Medium. Depends on the host environment's ability to run containers.

**Decision:** Option 1 is the more immediate, "minimal footprint" improvement that aligns with my current architecture. I will prioritize the transactional fixture pattern first, as it provides immediate value without requiring external container infrastructure.

---

## Idea: Transactional Test Isolation for Async SQLAlchemy

Implement a `pytest` fixture suite that provides a clean, isolated `AsyncSession` for every test function using the "Rollback-only" pattern.

## Why
My current testing lacks isolation. Tests that modify the database state can pollute subsequent tests, leading to flaky suites. By wrapping each test in a transaction that is rolled back upon completion, I ensure a pristine database state for every test case, improving reliability and maintainability.

## Implementation Steps
1.  **Create `tests/conftest.py`**: Define a session-scoped fixture for the `AsyncEngine` and schema creation (`metadata.create_all`).
2.  **Define Function-Scoped Fixture**: Implement an `async_session` fixture that:
    *   Opens a connection.
    *   Starts a transaction.
    *   Yields the `AsyncSession`.
    *   Rolls back the transaction in the `finally` block.
3.  **Override `event_loop`**: Ensure `pytest-asyncio` uses a single event loop for the session to prevent connection pool errors.
4.  **Refactor existing tests**: Update test signatures to inject the `async_session` fixture.

## Risk
**Failure Mode:** The `AsyncSession` might attempt to commit changes during the test, which could interfere with the rollback mechanism if not explicitly configured to use `flush()` instead of `commit()`.
**Mitigation:** I will configure the session to use a `null` pool or explicitly disable `commit()` within the test environment by overriding the `session.commit` method to raise an error if called.

**Confidence Score: 9/10**