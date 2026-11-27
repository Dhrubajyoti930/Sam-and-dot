## Scratchpad

**Option 1: Functor-based Error Handling (Monadic Result Pattern)**
*   **Concept:** Replace `None` or `try/except` blocks in `sam.py` with a `Result` container (Success/Failure) that implements `map` and `flatMap`.
*   **Critique:** High architectural alignment with the "Category Theory" skill learned. It forces explicit error handling. However, it requires a significant refactor of `ask_gemini` and `_parse_gemini_json`, which are critical paths.
*   **Feasibility:** Moderate. High risk of breaking existing patch-application logic if not handled carefully.

**Option 2: Semantic Deduplication Engine (Phase IV Objective)**
*   **Concept:** Implement a `deduplicate_experiences()` function that uses vector similarity (via `bag/semantic_cache.py`) to prune redundant entries in `experiences.json` before saving.
*   **Critique:** Directly addresses the "Semantic Deduplication" objective in `goals.json`. It keeps the memory footprint lean and improves the quality of context provided to Gemini in future cycles.
*   **Feasibility:** High. It leverages existing infrastructure (`semantic_cache`) and is non-destructive if implemented as a pre-save filter.

**Selection:** Option 2. It is a targeted, high-leverage improvement that directly fulfills a stated goal and improves the quality of my long-term memory.

---

## Idea: Semantic Experience Deduplication
Implement a pre-save filter in `phase_vii_state_saving` that checks new experience entries against existing ones using cosine similarity. If an entry is semantically redundant (similarity > 0.9), it is merged or discarded.

## Why
My `experiences.json` is growing. Redundant entries dilute the context provided to Gemini during `phase_iv_synthesis`, leading to repetitive planning. Deduplication ensures that my "long-term memory" remains high-signal.

## Implementation Steps
1.  **Modify `bag/semantic_cache.py`**: Expose a `get_similarity(text1, text2)` function using the existing vector DB.
2.  **Update `sam.py`**: In `phase_vii_state_saving`, before appending to `experiences.json`, iterate through the last 10 entries.
3.  **Filter Logic**: If `get_similarity(new_entry, existing_entry) > 0.9`, skip the append or update the existing entry with a "last_updated" timestamp.
4.  **Integrity**: Ensure `save_experiences` remains atomic.

## Risk
**Failure Mode:** The similarity threshold (0.9) might be too aggressive, causing the loss of nuanced, distinct experiences that happen to be phrased similarly.
**Mitigation:** Set the threshold to 0.92 and log every "deduplication event" to `log.info` so I can audit if I am losing valuable data.

## Self-Correction
*Critique:* Simply discarding entries might lose the "evolution" aspect of my growth.
*Refinement:* Instead of discarding, I will append a `merged_count` integer to the existing entry and update its `timestamp`. This preserves the frequency of the experience without bloating the file.

**Confidence Score: 9/10**