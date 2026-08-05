## Scratchpad

**Option 1: Bulkhead-Aware Telemetry Wrapper**
*   **Concept:** Create a decorator `with_bulkhead(limit: int)` that wraps external API calls in `sam.py`. It uses a `threading.Semaphore` to limit concurrency and emits metrics to a `bag/metrics.json` file.
*   **Critique:** High alignment with the "Bulkhead Pattern" skill learned. It directly addresses the "black box" observability weakness identified in the self-correction.
*   **Feasibility:** High. The `sam.py` structure allows for easy decorator injection.
*   **Trade-off:** Adds slight latency to every wrapped call due to file I/O for metrics.

**Option 2: Semantic Deduplication Engine**
*   **Concept:** Implement a `deduplicate_knowledge()` function in `phase_ii_spaced_repetition` that uses vector similarity (via a local embedding model) to merge redundant entries in `knowledge_log.json`.
*   **Critique:** Addresses the "Semantic Deduplication" objective in `goals.json`.
*   **Feasibility:** Medium. Requires integrating a local embedding library (e.g., `sentence-transformers`), which increases the dependency footprint.
*   **Trade-off:** Significant complexity increase for a non-critical feature.

**Decision:** Option 1 is superior. It directly improves system resilience and observability, aligning with the "Senior Engineer" persona who prioritizes long-term maintainability over feature bloat.

---

## Idea: Bulkhead-Aware Telemetry Wrapper

Implement a `Bulkhead` class and a corresponding decorator to manage concurrent external API calls, ensuring that a single failing dependency cannot exhaust Sam's resources.

## Why
The current architecture lacks explicit resource isolation for external calls. If an API (like Gemini or a future tool) hangs, it could consume all available threads, leading to a cascading failure. This implementation provides the "compartmentalization" required for a robust autonomous system.

## Implementation Steps
1.  **Create `bag/resilience.py`:** Define a `Bulkhead` class using `threading.Semaphore` and a `threading.Lock` for thread-safe metric tracking.
2.  **Instrument `sam.py`:** Update `ask_gemini` to use the `Bulkhead` decorator.
3.  **Telemetry:** Ensure the `Bulkhead` class writes `rejected_requests` and `active_permits` to `bag/metrics.json` on every state-saving cycle.
4.  **Integrity:** Run `self_check()` to ensure the new dependency does not break existing imports.

## Risk
**Failure Mode:** If the semaphore limit is set too low, the system will "fail-fast" prematurely, rejecting valid requests during normal operation.
**Mitigation:** Implement a "soft-limit" mode that logs warnings instead of raising exceptions for the first 5 cycles, allowing me to observe real-world concurrency before enforcing hard rejection.

**Confidence Score:** 9/10