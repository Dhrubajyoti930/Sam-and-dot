## Scratchpad

### Option 1: Implementing "Shadow Mode" for Patch Validation
*   **Concept:** Before applying a patch to the live `sam.py` or `workshop_bench/`, the system generates a temporary "shadow" environment, applies the patch, and runs the full test suite.
*   **Critique:** High safety, but high overhead. It requires a robust way to clone the current state (including `bag/` data) without side effects.
*   **Trade-off:** Increases cycle time significantly but provides near-zero risk of breaking the production state.

### Option 2: Implementing "Semantic Deduplication" for Memory
*   **Concept:** As the `experiences.json` grows, Sam risks repeating patterns. I will implement a vector-based deduplication layer that checks if a proposed "new" experience is semantically redundant with the last 50 cycles.
*   **Critique:** Improves the quality of the `experiences` log and forces me to seek novel challenges rather than re-treading old ground.
*   **Trade-off:** Requires a small embedding call, but significantly improves the long-term "wisdom" density of the system.

**Decision:** Option 2. It aligns with the "Disciplined Curiosity" trait and ensures my growth remains non-linear.

---

## Idea: Semantic Experience Deduplication
Implement a `deduplicate_experience` function that uses a lightweight cosine similarity check against the last 20 entries in `experiences.json` before committing a new entry in Phase VII.

## Why
My growth log is becoming a repository of "what I did" rather than "what I learned." By filtering for semantic novelty, I force myself to prioritize unique, high-value technical challenges over routine maintenance, ensuring my 1% growth metric remains meaningful.

## Implementation Steps
1.  **Update `bag/`:** Create `bag/semantic_utils.py` with a simple cosine similarity function using `numpy` (or a basic dot product if avoiding heavy dependencies).
2.  **Refactor `phase_vii_state_saving`:** Before appending to `experiences.json`, call the deduplicator.
3.  **Thresholding:** If similarity > 0.85, trigger a "Refinement" flag instead of a "New Experience" entry, forcing the system to summarize the existing knowledge rather than creating a redundant log.

## Risk
**Failure Mode:** The similarity threshold might be too aggressive, causing me to discard valid, iterative learning steps that are distinct enough to warrant a log.
**Mitigation:** Implement a "Force Log" override if the `growth_log` indicates a significant change in the `next_objectives` list, ensuring that even if the content is similar, the context of the objective is preserved.

**Confidence Score:** 9/10