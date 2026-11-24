## Scratchpad

**Option 1: Implement a "Regex-to-DFA" Compiler Utility**
*   **Concept:** Build a module in `workshop_bench/` that uses `sre_parse` to convert Python regex patterns into a state-transition table (DFA) for performance-critical log parsing.
*   **Critique:** High technical value, aligns with the "Finite Automata" skill learned. However, it risks "reinventing the wheel" poorly. Python's `re` module is already highly optimized C.
*   **Trade-off:** Better performance for specific, repetitive patterns vs. high maintenance burden for the state-machine logic.

**Option 2: Semantic Deduplication Engine (Phase IV Objective)**
*   **Concept:** Use the existing `bag/semantic_cache.py` to compare new `knowledge_log` entries against historical ones using cosine similarity, flagging redundant learning cycles.
*   **Critique:** Directly addresses the "Semantic Deduplication" objective in `goals.json`. It improves the quality of the knowledge base without adding external dependencies.
*   **Trade-off:** Requires careful threshold tuning to avoid false negatives (flagging distinct but related concepts as duplicates).

**Selection:** Option 2. It directly fulfills a pending objective and leverages existing infrastructure, maintaining Sam's "minimal footprint" philosophy.

---

## Idea: Semantic Knowledge Deduplication (Phase IV)

Implement a similarity-check gate in `phase_i_deep_learning` that compares the current `focus` topic against the `knowledge_log.json` history before initiating a full Gemini call.

## Why
Sam’s knowledge base is growing. To maintain high-density learning, Sam must avoid re-learning concepts he has already mastered. This reduces API costs and ensures the `knowledge_log` remains a curated index of unique insights rather than a collection of redundant summaries.

## Implementation Steps
1.  **Modify `phase_i_deep_learning`:** Add a call to a new helper `_is_redundant(topic: str) -> bool`.
2.  **Create `bag/semantic_utils.py`:** Implement a function that retrieves embeddings for the current `focus` and compares them against the stored summaries in `knowledge_log.json` using the existing semantic cache database.
3.  **Threshold Logic:** If similarity > 0.85, log a "Redundancy Detected" warning and select the next objective from `goals.json` instead of proceeding.
4.  **Update `goals.json`:** If redundant, increment the cycle count and skip the learning phase to save resources.

## Risk
**Failure Mode:** The similarity threshold is too aggressive, causing Sam to skip valid, nuanced learning on a topic he has only touched superficially.
**Mitigation:** Set the initial threshold high (0.90) and log the "skipped" topic to a `skipped_learning.json` file for manual review by Dot, ensuring no data is permanently lost.

**Confidence Score:** 9/10