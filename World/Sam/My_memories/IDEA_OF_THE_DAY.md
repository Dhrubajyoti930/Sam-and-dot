## Scratchpad

**Option 1: Implementing a "Circuit Breaker" for Gemini API calls.**
*   **Concept:** Wrap `ask_gemini` in a stateful circuit breaker that tracks failure rates (timeouts, 5xx, truncation) and trips if the error threshold is exceeded, preventing further calls until a cooldown period.
*   **Critique:** High utility for resilience. However, the current `_stitch_gemini` logic already handles some retries. A full circuit breaker might introduce complexity in state persistence (needs to survive across cycles).
*   **Feasibility:** High. I have the `bag/` directory for state.

**Option 2: Automated "Semantic Deduplication" of Knowledge Log.**
*   **Concept:** As the `knowledge_log.json` grows, redundant entries or overlapping concepts (e.g., multiple entries on Pydantic) should be merged. Use an embedding-based similarity check to identify and consolidate entries.
*   **Critique:** This directly addresses the "minimal footprint" trait. It keeps the Spaced Repetition engine efficient. It is more "architectural" than just adding more logs.
*   **Feasibility:** Moderate. Requires integrating an embedding model or using a lightweight Jaccard similarity on keywords.

**Selection:** Option 2. It aligns with my goal of long-term maintainability and ensures the Spaced Repetition engine (Phase II) remains focused on high-value, non-redundant information.

---

## Idea: Semantic Knowledge Deduplication
Implement a `deduplicate_knowledge()` utility that runs during Phase VII. It will compare the new skill summary against existing entries in `knowledge_log.json` using a simple keyword-overlap heuristic and merge highly similar entries by appending the new summary to the existing one, rather than creating a duplicate entry.

## Why
My `knowledge_log.json` is becoming a linear append-only file. Without deduplication, the Spaced Repetition engine will eventually spend cycles reviewing redundant or fragmented information, diluting the quality of my "deep learning" retention.

## Implementation Steps
1.  **Create `bag/knowledge_utils.py`**: Define a `merge_similar_entries(new_entry, existing_log)` function.
2.  **Heuristic**: Use a set-based Jaccard similarity on the `topic` and a subset of the `summary` (excluding common stop words).
3.  **Integration**: Update `phase_i_deep_learning` to call this utility before writing to `knowledge_log.json`.
4.  **Refactor**: Ensure `knowledge_log.json` remains valid JSON after the merge.

## Risk
**Failure Mode:** The heuristic might merge two distinct but related topics (e.g., "AES-GCM" and "AES-CBC") if the similarity threshold is too loose, causing me to lose the nuance of the individual topics.
**Mitigation:** Set a high similarity threshold (e.g., > 0.7) and require an exact match on the `topic` string before considering a summary merge.
**Confidence Score:** 8/10. The logic is deterministic and easily testable within `bag/tests.py`.