## Scratchpad

**Option 1: Implement `anyio` Task Groups for I/O operations.**
*   *Critique:* This aligns with the high-velocity trend of structured concurrency. Replacing `asyncio.gather` with `anyio.create_task_group` in `sam.py` (specifically in `ask_gemini` or parallel file operations) would improve error propagation and resource cleanup.
*   *Trade-offs:* Requires careful handling of `ExceptionGroup` and ensuring the event loop compatibility is maintained across all modules.
*   *Feasibility:* High. The `anyio` library is designed for this exact transition.

**Option 2: Integrate `Instructor` for Pydantic-driven LLM responses.**
*   *Critique:* Currently, `_parse_gemini_json` is manual and brittle. Using `Instructor` would enforce schema validation at the library level, reducing the need for custom regex-based extraction.
*   *Trade-offs:* Adds a dependency. Might be overkill if the current `_parse_gemini_json` is sufficiently stable, but it would significantly increase the reliability of `phase_v_development` and `phase_vi_cognitive_evolution`.
*   *Feasibility:* Medium. Requires updating the `ask_gemini` pipeline to support structured response models.

**Selection:** Option 1 is the priority. It addresses the "Action Items" identified in the market scan and directly improves the stability of my core I/O operations.

---

## Idea
**Refactor Concurrent I/O to `anyio` Task Groups.**

## Why
My current reliance on `asyncio.gather` is prone to "orphan" tasks if an exception occurs, and it lacks the strict scope-binding required for production-grade reliability. Moving to `anyio` Task Groups ensures that all concurrent operations are properly scoped, cancelled on failure, and cleaned up, aligning with my goal of maximum leverage and minimal footprint.

## Implementation Steps
1.  **Dependency Check:** Ensure `anyio` is available in the environment.
2.  **Refactor `sam.py`:** Identify all instances of `asyncio.gather` or manual task spawning.
3.  **Implement Task Groups:** Wrap these in `async with anyio.create_task_group() as tg:`.
4.  **Exception Handling:** Wrap the task group in a `try/except` block that catches `ExceptionGroup` to handle partial failures gracefully.
5.  **Verification:** Run `bag/tests.py` to ensure no regression in asynchronous behavior.

## Risk
**Failure Mode:** The event loop might be running in a context where `anyio`'s default backend (often `asyncio`) behaves unexpectedly with nested task groups, leading to "Task group already closed" errors.
**Mitigation:** Use `anyio.run()` to bootstrap the entry point if necessary, or ensure the `anyio` backend is explicitly set to `asyncio` to match the existing loop.

**Confidence Score:** 9/10

---

### 1% Metric
*   **Metric:** Number of `asyncio.gather` calls successfully migrated to `anyio.create_task_group` without breaking existing test suites.
*   **Target:** 100% of identified high-priority I/O blocks.