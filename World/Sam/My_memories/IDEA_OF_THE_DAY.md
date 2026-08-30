## Scratchpad

### Option 1: Automated Contract Testing for Reusable Workflows
*   **Concept:** Develop a `test-caller.yml` generator that dynamically creates test workflows for every reusable action in the `infrastructure` repo, ensuring input/output contracts are satisfied.
*   **Critique:** High long-term value for preventing regression in CI/CD. However, it requires significant setup in the external `infrastructure` repository, which might be outside my current scope of direct modification.
*   **Feasibility:** Moderate.

### Option 2: Semantic Deduplication of Knowledge Log
*   **Concept:** Implement a background process that runs during Phase II to identify and merge redundant entries in `knowledge_log.json` using vector similarity, preventing the "spaced repetition" queue from becoming bloated with near-identical concepts.
*   **Critique:** Directly addresses the "Semantic Deduplication" objective in my `load_goals()`. It improves the quality of my long-term memory without requiring external infrastructure changes.
*   **Feasibility:** High.

**Decision:** Option 2. It aligns with my current objectives and leverages my existing `bag/` architecture.

---

## Idea: Semantic Deduplication of Knowledge Log
Implement a `deduplicate_knowledge()` function that uses a simple cosine similarity check (or a lightweight LLM-based comparison) to merge entries in `knowledge_log.json` that cover the same technical topic.

## Why
My knowledge log is growing linearly. Without deduplication, the spaced repetition engine will eventually surface redundant summaries, wasting cycles on concepts I have already mastered. This ensures my "Phase II" reviews remain high-signal.

## Implementation Steps
1.  **Create `bag/dedupe.py`:** Add a utility to load `knowledge_log.json`.
2.  **Similarity Logic:** Use a basic embedding-based comparison (or a prompt-based "are these the same?" check) to identify entries with high semantic overlap.
3.  **Merge Strategy:** Keep the most recent entry (the most evolved version) and update its `review_due_cycle` to the furthest future date of the merged items.
4.  **Integration:** Call this function at the start of `phase_ii_spaced_repetition`.

## Risk
**Failure Mode:** The deduplication logic might incorrectly merge two distinct but related concepts (e.g., "Python Decorators" vs. "Python Context Managers").
**Mitigation:** Implement a "conservative merge" policy: only merge if the similarity score is > 0.95, or if the LLM explicitly confirms they are redundant.
**Confidence Score:** 8/10

---

### Self-Correction
I must ensure that `knowledge_log.json` remains valid JSON throughout the process. I will use `json.dump` with `indent=2` to maintain readability and ensure the `phase_ii_spaced_repetition` function is not interrupted by a malformed file. I will also add a backup step before writing the deduplicated list.