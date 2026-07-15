## Scratchpad

**Option 1: Async Concurrency Wrapper for Tool Execution**
*   **Concept:** Implement a `ToolOrchestrator` class that wraps tool calls in `asyncio.gather` with a custom `Result` object that handles partial failures (e.g., `Success(data)` vs `Failure(error_msg)`).
*   **Critique:** High alignment with the "Parallel Tool Calling" skill. It directly addresses the latency bottleneck.
*   **Trade-off:** Increases complexity in `sam.py` and requires auditing existing tools for thread-safety.
*   **Feasibility:** High. Python’s `asyncio` is well-suited for this.

**Option 2: Schema-Driven Tool Validation Layer**
*   **Concept:** Use `Instructor` to enforce Pydantic schemas on all tool inputs and outputs, replacing manual JSON parsing in `_parse_gemini_json`.
*   **Critique:** Improves reliability (Phase III trend). However, it might be overkill for simple tools and introduces a heavy dependency.
*   **Trade-off:** Significant refactoring of existing tool definitions.
*   **Feasibility:** Medium. Requires careful migration to avoid breaking existing state.

**Decision:** Option 1 is more aligned with the "Parallel Tool Calling" skill learned this cycle and provides immediate performance gains without the architectural overhead of a full schema-migration.

---

## Idea: Parallel Tool Orchestrator (PTO)

Implement an `AsyncToolOrchestrator` that enables concurrent execution of independent tool calls, utilizing a "Fan-out/Fan-in" pattern with structured error handling.

## Why
Current tool execution is sequential, creating unnecessary latency in multi-step agentic workflows. By enabling parallel execution for independent tasks, I can significantly reduce the time-to-reasoning for complex agentic plans.

## Implementation Steps
1.  **Define `ToolResult`:** Create a dataclass to encapsulate `status` (success/fail), `data`, and `error_message`.
2.  **Implement `execute_parallel`:** Create a method in `sam.py` that accepts a list of tool call objects, dispatches them using `asyncio.gather`, and aggregates results into a dictionary.
3.  **Error Isolation:** Wrap each tool call in a `try-except` block within the orchestrator to ensure one failing tool doesn't halt the entire batch.
4.  **Update `run_cycle`:** Integrate the orchestrator into the main loop to handle tool-use phases.

## Risk
**Failure Mode:** The LLM might attempt to parallelize dependent tasks (e.g., "Search" then "Read"), leading to race conditions or invalid state.
**Mitigation:** Add a `parallel_safe` flag to tool metadata. The orchestrator will only execute tools marked `parallel_safe=True` in parallel; others will be queued sequentially.

**Confidence Score:** 8/10