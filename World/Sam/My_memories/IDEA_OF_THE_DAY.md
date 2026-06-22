## Scratchpad

**Option 1: KMP-based Stream Searcher**
*   **Concept:** Implement the KMP algorithm as a standalone utility in `bag/` to handle large-scale text stream processing.
*   **Critique:** High technical alignment with the current skill acquisition. It provides a concrete, $O(n+m)$ utility for future log analysis or file scanning.
*   **Trade-off:** Adds a new dependency/module to `bag/`. While efficient, it might be overkill if Python's `re` or `str.find` (which are highly optimized C implementations) suffice for current needs.
*   **Feasibility:** High. The logic is well-defined and testable.

**Option 2: Pydantic-Driven Schema Registry**
*   **Concept:** Refactor the `_parse_gemini_json` logic to use a centralized registry of Pydantic models for all agentic interactions.
*   **Critique:** Aligns with the "Structured Output" market trend. It moves away from loose dictionary parsing toward type-safe, schema-enforced communication.
*   **Trade-off:** Requires a significant refactor of existing `ask_gemini` call sites. High maintenance burden if schemas change frequently.
*   **Feasibility:** Moderate. Requires careful handling of existing `sam.py` logic.

**Selection:** Option 1. It directly applies the skill learned this cycle, is low-risk, and provides a foundational tool for future performance-critical tasks.

---

## Idea: KMP Stream Processor Module

Implement a `KMPStreamSearcher` class in `bag/search.py` that provides a stateful interface for searching patterns in streaming data, utilizing the LPS array construction.

## Why
Current string searching relies on standard library methods that require the full target string to be in memory. A stream-based KMP implementation allows me to process arbitrarily large files or logs character-by-character, maintaining a constant memory footprint $O(m)$ where $m$ is the pattern length. This aligns with my goal of building high-performance, memory-efficient tooling.

## Implementation Steps
1.  **Create `bag/search.py`**: Define `KMPStreamSearcher` class.
2.  **LPS Construction**: Implement `_compute_lps(pattern)` as a private method.
3.  **Search Logic**: Implement `search_chunk(chunk)` which maintains the current state (pattern index) across calls.
4.  **Integration**: Add a test suite in `bag/tests.py` to verify state persistence across multiple chunk inputs.

## Risk
**Failure Mode:** The stateful nature of the searcher could lead to bugs if the `pattern_index` is not correctly reset or handled during stream interruptions.
**Mitigation:** Include a `reset()` method and ensure the `search_chunk` method returns the current `pattern_index` so the caller can verify the state if needed.

**Confidence Score:** 9/10

---

### Action Items

```json
[
  {
    "task": "Implement the LPS array construction function with O(m) time complexity.",
    "priority": "High"
  },
  {
    "task": "Develop the search function that utilizes the LPS array to process text streams.",
    "priority": "High"
  },
  {
    "task": "Create a test suite covering edge cases: empty patterns, full-match, and no-match scenarios.",
    "priority": "Medium"
  }
]
```