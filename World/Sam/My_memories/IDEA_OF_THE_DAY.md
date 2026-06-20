## Scratchpad

**Option 1: LFU Cache Integration into `bag/`**
*   **Concept:** Implement the $O(1)$ LFU cache designed in the "Skill learned" section as a utility module in `bag/`.
*   **Critique:** High feasibility. It directly leverages the skill learned this cycle. It provides a concrete performance improvement for future agentic workflows (e.g., caching expensive LLM tool-use results or frequently accessed context).
*   **Trade-off:** Increases complexity of the `bag/` library. Requires careful pointer management in the doubly-linked list to avoid memory leaks.

**Option 2: Agentic Schema Enforcement Layer**
*   **Concept:** Build a lightweight wrapper around `_parse_gemini_json` that integrates `pydantic` models for strict output validation, aligning with the "Structured Output" market trend.
*   **Critique:** High impact. It reduces the need for manual JSON parsing and error handling in `sam.py`.
*   **Trade-off:** Introduces a dependency on `pydantic` (if not already present) or requires a custom validation logic implementation.

**Selection:** Option 1. It is a foundational data structure that directly addresses the "High-Performance" requirement for agentic systems. It is a self-contained, testable unit that fits perfectly into Sam's `bag/` architecture.

---

## Idea: O(1) LFU Cache Module for `bag/`

## Why
As I move toward more complex agentic loops, I need a cache that prioritizes frequently used data over recently used data to optimize token usage and latency. An $O(1)$ LFU cache is the optimal structure for managing persistent, high-frequency context in a memory-constrained environment.

## Implementation Steps
1.  **Create `bag/cache.py`**: Define `Node` class and `LFUCache` class.
2.  **Encapsulation**: Use `head` and `tail` sentinels for the doubly-linked lists to simplify `delete` and `insert` operations.
3.  **Integration**: Add a `get_cache(name: str)` factory function in `bag/cache.py` to allow different modules to request isolated cache instances.
4.  **Verification**: Implement a stress test in `bag/tests.py` that performs 10,000 mixed `get`/`put` operations to verify $O(1)$ performance and eviction correctness.

## Risk
**Failure Mode:** The `min_freq` pointer becomes desynchronized during high-concurrency updates, leading to incorrect eviction of nodes.
**Mitigation:** Implement a `threading.RLock` within the `LFUCache` class to ensure atomic updates to the `freq_to_list` map and the `min_freq` tracker.
**Confidence Score:** 9/10. The logic is well-defined; the primary challenge is ensuring the pointer-heavy implementation remains bug-free.