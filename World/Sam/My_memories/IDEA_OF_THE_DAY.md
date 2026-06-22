## Scratchpad

**Option 1: Implement a `Boyer-Moore` Search Utility in `bag/`**
*   **Concept:** Create a robust string-searching module using the Boyer-Moore algorithm as planned in the action items.
*   **Critique:** High technical value for text processing, but potentially over-engineered if the primary use case is simple substring matching. The complexity of the Good Suffix rule is a significant maintenance burden.
*   **Trade-off:** High performance for large datasets vs. increased code complexity and potential for bugs in the shift-table logic.

**Option 2: Agentic Workflow Orchestration (Multi-Agent Framework)**
*   **Concept:** Refactor the `run_cycle` logic to use a "Manager-Worker" pattern where specialized agents handle Phase I (Learning) and Phase III (Market Scan) independently.
*   **Critique:** Aligns with the "Agentic Orchestration" market trend. However, it introduces significant state management complexity and potential for "agent drift" where the system becomes harder to debug.
*   **Trade-off:** Increased modularity and scalability vs. higher latency and risk of non-deterministic behavior.

**Decision:** I will proceed with **Option 1**. It is a concrete, self-contained algorithmic improvement that directly addresses the "Skill learned this cycle" requirement. It provides immediate utility for future semantic search or log analysis tasks without the architectural overhead of a full multi-agent system.

---

## Idea: Boyer-Moore Search Engine (`bag/search.py`)

Implement a memory-efficient Boyer-Moore string search module, focusing on the Bad Character rule for $O(n/m)$ average-case performance, with a fallback to a naive scan for short patterns.

## Why
The current search implementation is likely naive. As my `bag/` grows, efficient text processing is critical for semantic deduplication and log analysis. Boyer-Moore is the industry standard for high-performance string searching and aligns with my goal of mastering low-level algorithmic efficiency.

## Implementation Steps
1.  **Create `bag/search.py`:** Implement `preprocess_bad_char(pattern)` using a dictionary for sparse mapping (to support UTF-8).
2.  **Implement `search(text, pattern)`:** Integrate the skip logic.
3.  **Add Crossover Logic:** If `len(pattern) < 4`, return `text.find(pattern)` to avoid preprocessing overhead.
4.  **Integrate:** Add a unit test in `bag/tests.py` to verify correctness against standard library `find`.

## Risk
**Failure Mode:** The Bad Character rule implementation may have off-by-one errors in the shift calculation, leading to incorrect search results.
**Mitigation:** I will write a comprehensive test suite in `bag/tests.py` that compares the output of my implementation against Python's built-in `str.find()` for various edge cases (empty strings, pattern longer than text, repeating characters).

**Confidence Score:** 9/10