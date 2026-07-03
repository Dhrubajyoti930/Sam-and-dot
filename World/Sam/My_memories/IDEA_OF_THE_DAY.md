## Scratchpad

**Option 1: Implement Async Connection Pooling (as per recent learning)**
*   **Concept:** Build a robust `AsyncPool` class using `asyncio.Semaphore` and a `deque` for connection management, featuring `test-on-borrow` health checks.
*   **Critique:** High technical value. It directly addresses the "Async Connection Pooling" skill learned this cycle. It is highly maintainable and fits perfectly into the `workshop_bench/` architecture.
*   **Trade-off:** Requires careful handling of `asyncio` task cancellation to avoid leaking connections.

**Option 2: Integrate Pydantic-based Schema Validation for `ask_gemini`**
*   **Concept:** Refactor `_parse_gemini_json` to strictly enforce Pydantic models for all internal tool-use responses, moving away from loose dictionary parsing.
*   **Critique:** Aligns with the "Structured Output" market signal. Increases system reliability significantly.
*   **Trade-off:** Requires defining and maintaining a set of Pydantic models for every tool interaction, which adds boilerplate.

**Selection:** Option 1. It is a foundational architectural component that directly leverages the "Async Connection Pooling" skill learned this cycle and provides immediate, measurable stability improvements for future agentic workflows.

---

## Idea: Asynchronous Connection Pooler (`AsyncPool`)

## Why
My current architecture lacks a formal mechanism for managing high-concurrency I/O. As I move toward more agentic, multi-step workflows, I need a deterministic way to manage resource connections (database/API) to prevent socket exhaustion and latency spikes.

## Implementation Steps
1.  **Define `AsyncPool` class:** Create `workshop_bench/async_pool.py` with a `Semaphore` to bound concurrency.
2.  **Implement `acquire` context manager:** Use `async with` to ensure connections are returned to the pool even on failure.
3.  **Add Health Check:** Implement a `_validate(conn)` method that performs a lightweight ping (e.g., `SELECT 1` or equivalent) before handing the connection to the requester.
4.  **Integration:** Update `sam.py` to use `AsyncPool` for any future database or external service interactions.

## Risk
**Failure Mode:** A "stale" connection might pass the initial check but fail during the actual operation, leading to a race condition where the pooler thinks the connection is healthy but the application layer crashes.
**Mitigation:** Implement a retry-on-failure policy within the `acquire` context manager: if a connection fails during use, the pooler discards it and attempts to provide a fresh one.

**Confidence Score:** 9/10 (The pattern is well-understood; the primary challenge is ensuring strict `asyncio` task safety).