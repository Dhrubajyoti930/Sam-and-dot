## Scratchpad

**Option 1: Automated Dependency Coupling Score (DCS) Monitoring**
*   **Concept:** Integrate a script that calculates the DCS for `workshop_bench/` modules after every `apply_patch_operations` call. If a patch increases the coupling beyond a threshold, Sam flags it for review.
*   **Critique:** High value for long-term maintainability. However, calculating graph-based metrics (DCS) requires a robust parser for imports and internal references. It risks becoming a "God Object" itself if not kept lightweight.
*   **Feasibility:** Moderate. Requires building a dependency graph from ASTs.

**Option 2: Semantic Cache "Self-Healing" via Vector Similarity**
*   **Concept:** When `ask_gemini` returns a result that fails the `self_check` or `behaviour_check`, instead of just rolling back, Sam queries the semantic cache for "successful" past responses to similar prompts and attempts to synthesize a fix based on those patterns.
*   **Critique:** This moves Sam toward "experience-based" self-correction. It is more sophisticated than a simple rollback.
*   **Feasibility:** High, as the infrastructure for `semantic_cache` already exists. It leverages the existing `bag/semantic_cache.py`.

**Decision:** Option 2 is more aligned with Sam's goal of autonomous improvement. It turns failure into a data-gathering exercise rather than just a reset.

---

## Idea: Semantic Cache "Failure-Context" Injection
Implement a mechanism where, upon a `behaviour_check` failure, Sam retrieves the top 3 most similar successful prompts from the `semantic_cache` and injects their "correction patterns" into the `_behaviour_fix_with_gemini` prompt.

## Why
Currently, when Sam fails a test, he asks Gemini to fix it from scratch. By providing examples of *how* he previously resolved similar logic errors or structural issues, he reduces the "hallucination" rate of the fix and accelerates the learning curve for complex architectural changes.

## Implementation Steps
1.  **Update `_behaviour_fix_with_gemini`:** Add a call to `check_cache` (or a new similarity search function) using the current failing test output as the query.
2.  **Context Construction:** Format the retrieved successful patches into a "Historical Correction Patterns" section in the prompt sent to Gemini.
3.  **Prompt Refinement:** Instruct Gemini to "Use these historical patterns as a guide for the current fix."
4.  **Logging:** Log whether the fix was successful using the historical context to track if this actually improves the 1% growth metric.

## Risk
**Failure Mode:** The retrieved "successful" patterns might be contextually irrelevant to the current failure, leading Gemini to apply outdated or incorrect logic (e.g., trying to fix a syntax error with a logic-patch pattern).
**Mitigation:** Implement a strict similarity threshold (cosine distance) for the cache retrieval. If no high-confidence matches are found, skip the injection and proceed with standard repair.

**Confidence Score:** 8/10