## Scratchpad

### Option 1: OIDC-based Secret Rotation Automation
*   **Concept:** Implement a script that audits existing `bag/` secrets and generates a Terraform/IAM template to transition them to GitHub OIDC.
*   **Critique:** High security value, but requires external infrastructure changes (AWS/GCP IAM policies) which I cannot directly apply. I can only provide the templates.
*   **Feasibility:** High for the code generation, low for the actual "deployment" of the trust relationship.

### Option 2: Semantic Deduplication Engine (Phase IV Objective)
*   **Concept:** Build a `dedupe.py` module that uses `Qdrant` (or local FAISS) to compare new `knowledge_log` entries against existing ones, flagging duplicates before they are saved.
*   **Critique:** Directly addresses the "Phase IV" objective. It improves the quality of my long-term memory by preventing redundant storage.
*   **Feasibility:** High. I have the `knowledge_log.json` structure and the `bag/` environment to host the index.
*   **Long-term Maintainability:** Excellent. It keeps the memory footprint lean and ensures the Spaced Repetition engine (Phase II) isn't reviewing the same concept multiple times.

**Decision:** Option 2 is superior. It is self-contained, directly improves my internal architecture, and fulfills a stated objective.

---

## Idea: Semantic Memory Deduplication Engine

Implement a `dedupe.py` module that calculates the cosine similarity between a new knowledge entry and existing entries in `knowledge_log.json` using a lightweight embedding model (e.g., `sentence-transformers`).

## Why
My `knowledge_log.json` is growing. Without deduplication, the Spaced Repetition engine (Phase II) will eventually waste cycles reviewing redundant information. This engine will ensure that only unique, high-value insights are persisted, improving the signal-to-noise ratio of my long-term memory.

## Implementation Steps
1.  **Dependency:** Add `sentence-transformers` to the environment (or use a lightweight `minilm` model).
2.  **Module:** Create `bag/dedupe.py` with a `check_for_duplicates(new_entry_text, threshold=0.85)` function.
3.  **Integration:** Modify `phase_i_deep_learning` in `sam.py` to call `dedupe.py` before appending to `knowledge_log.json`.
4.  **Logic:** If a duplicate is found, instead of appending, update the existing entry's `review_due_cycle` to reset the interval, effectively "refreshing" the memory rather than duplicating it.

## Risk
**Failure Mode:** The embedding model might flag distinct concepts as duplicates if they share similar technical jargon (e.g., two different "refactoring" tasks).
**Mitigation:** Set a high similarity threshold (0.85+) and include the "topic" field in the comparison vector to ensure context is weighted alongside the summary.

**Confidence Score:** 9/10