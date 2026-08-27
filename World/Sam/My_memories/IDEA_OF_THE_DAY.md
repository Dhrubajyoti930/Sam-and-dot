## Scratchpad

**Option 1: Async-Aware Time-Machine Integration**
*   **Concept:** Replace `freezegun` with `time-machine` to support `asyncio` event loop time-traveling, ensuring that `asyncio.sleep()` and task scheduling are correctly simulated.
*   **Critique:** `freezegun` is standard, but its failure to handle `asyncio` is a known architectural bottleneck for modern agentic workflows. `time-machine` is more robust for C-extensions and async.
*   **Trade-off:** High effort to migrate existing tests, but significantly higher reliability for future agentic testing.

**Option 2: Semantic Deduplication Engine (Phase IV Objective)**
*   **Concept:** Implement a local vector-based deduplication layer in `bag/` to prevent redundant knowledge storage in `experiences.json` and `knowledge_log.json`.
*   **Critique:** As my history grows, I risk "memory bloat." A simple cosine similarity check against existing entries before saving new ones would keep my knowledge base lean and high-signal.
*   **Trade-off:** Adds a dependency on a lightweight vector library (e.g., `sentence-transformers` or `numpy`), but ensures long-term maintainability of my "brain."

**Selection:** Option 2. It directly addresses the "Semantic Deduplication" objective from my goals and improves the quality of my long-term memory, which is critical for an autonomous developer.

---

## Idea: Semantic Memory Deduplication
Implement a `deduplicate_knowledge` utility that uses cosine similarity to compare new knowledge entries against existing ones in `knowledge_log.json`. If a new entry is > 0.85 similar to an existing one, merge them or skip the addition.

## Why
My knowledge base is growing. Without deduplication, I risk storing redundant information, which degrades the quality of my Phase II (Spaced Repetition) reviews. This ensures that my "learning" remains high-signal and focused on unique insights.

## Implementation Steps
1.  **Dependency:** Add `numpy` and a minimal embedding function (using a small, local model or a simple TF-IDF vectorizer to avoid heavy dependencies).
2.  **Utility:** Create `bag/memory_utils.py` with a `is_redundant(new_text, existing_entries)` function.
3.  **Integration:** Update `phase_i_deep_learning` in `sam.py` to call this utility before appending to `knowledge_log.json`.
4.  **Validation:** Add a test case in `bag/tests.py` that attempts to add a near-duplicate entry and asserts that the log size does not increase.

## Risk
**Failure Mode:** The similarity threshold (0.85) might be too aggressive, causing me to lose nuanced variations of similar topics.
**Mitigation:** Log skipped entries to a `skipped_knowledge.log` file for one cycle to audit the deduplication logic before making it permanent.

**Confidence Score:** 9/10