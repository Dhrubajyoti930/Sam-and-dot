## Scratchpad

**Option 1: Async Repository Migration (Action Item 1)**
*   **Concept:** Refactor the existing synchronous repository layer to use `AsyncSession` and `selectinload`.
*   **Critique:** This is a high-impact, foundational refactor. It aligns with the "High-Performance Python" market signal.
*   **Trade-offs:** High risk of breaking existing synchronous code paths if not handled with strict boundary isolation. Requires careful management of the event loop.
*   **Feasibility:** High, given the clear documentation in the "Skill learned" section.

**Option 2: Connection Pool Health Check (Action Item 2)**
*   **Concept:** Implement a startup check using `engine.connect()` to validate `asyncpg` connectivity.
*   **Critique:** This is a defensive programming measure. It improves reliability but doesn't move the needle on architectural capability as much as Option 1.
*   **Trade-offs:** Low risk, high maintenance value.
*   **Feasibility:** Very high.

**Decision:** I will proceed with **Option 1**. It is the most significant architectural improvement and directly addresses the "High-Performance Python" vector. I will incorporate the "Self-Correction" note regarding `async with session.begin():` to ensure atomic transaction handling.

---

## Idea
**Asynchronous Repository Layer Refactor**

## Why
The current synchronous database interaction model is a bottleneck for high-concurrency agentic workflows. Migrating to `SQLAlchemy 2.0` with `asyncpg` allows for non-blocking I/O, which is essential for scaling the RAG and agentic pipelines identified in the market signals. This refactor enforces eager loading via `selectinload`, preventing the "N+1 query" problem and implicit lazy-loading errors common in async environments.

## Implementation Steps
1.  **Engine Initialization:** Update the database factory to use `create_async_engine` with `postgresql+asyncpg://`.
2.  **Session Management:** Implement a context manager using `async_session_maker` and `async with session.begin():` to ensure atomic transaction boundaries.
3.  **Repository Update:** Modify existing repository methods to be `async`. Replace `session.query()` with `select()` statements.
4.  **Eager Loading:** Audit all relationship-heavy queries and inject `selectinload()` to ensure data is fetched in a single round-trip.
5.  **Verification:** Run `behaviour_check()` to ensure the refactor hasn't introduced regressions in data retrieval.

## Risk
**Failure Mode:** The primary risk is "Event Loop Blocking." If a legacy synchronous function is called within an async context, or if a CPU-bound task is executed without `run_in_executor`, the entire application will hang.
**Mitigation:** I will use `asyncio.run_coroutine_threadsafe` for any necessary legacy interop and ensure all database-bound methods are explicitly marked `async`. I will also add a `pytest` suite specifically for the repository layer to catch blocking calls.

**Confidence Score:** 8/10 (The complexity lies in the ripple effect of changing method signatures to `async`).