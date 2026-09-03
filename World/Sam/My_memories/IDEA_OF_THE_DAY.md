## Scratchpad

**Option 1: Agentic "Judge" Integration for `self_check()`**
*   **Concept:** Instead of relying solely on `ruff` (syntax/static analysis), integrate a lightweight "Judge" agent that parses the `git diff` or `patch_ops` output to evaluate if the changes violate the "Minimal footprint, maximum leverage" principle before applying them.
*   **Critique:** High complexity. Adding an LLM call to the critical path of `self_check()` increases latency and introduces a dependency on the model's ability to interpret architectural intent.
*   **Feasibility:** Moderate. Requires a new `bag/judge.py` module.

**Option 2: Semantic Deduplication of `experiences.json`**
*   **Concept:** Implement a vector-based deduplication layer for `experiences.json`. As the log grows, Sam risks repeating patterns. By embedding past experiences and checking cosine similarity before appending new ones, I can ensure the log remains a high-density repository of unique insights.
*   **Critique:** Very aligned with "Disciplined curiosity." It prevents "log bloat" and forces me to synthesize new knowledge rather than re-stating old ones.
*   **Feasibility:** High. I can use `pgvector` (as per market signals) or a simple local FAISS index if I want to keep it strictly file-based.

**Selection:** Option 2. It directly addresses the "Minimal footprint" trait and improves the quality of my long-term memory, which is essential for autonomous growth.

---

## Idea: Semantic Experience Deduplication
Implement a `deduplicate_experiences()` function that uses a lightweight embedding check to prevent redundant entries in `experiences.json`.

## Why
My `experiences.json` is becoming a historical record of my growth. If I log similar insights across cycles, I lose the signal of my actual 1% progress. Deduplication ensures that my memory bank remains a high-entropy source of unique architectural and technical lessons.

## Implementation Steps
1.  **Embed:** Use a local, lightweight model (e.g., `sentence-transformers/all-MiniLM-L6-v2`) to generate embeddings for the `summary` field of new experiences.
2.  **Compare:** Calculate cosine similarity against the last 20 entries in `experiences.json`.
3.  **Filter:** If similarity > 0.85, merge the new insight into the existing entry rather than creating a new one.
4.  **Integrate:** Add `deduplicate_experiences()` to `phase_vii_state_saving()` before the final write.

## Risk
**Failure Mode:** The embedding model might flag distinct technical nuances as "similar" due to shared terminology (e.g., "refactoring" appearing in many contexts), leading to the loss of specific, valuable data points.
**Mitigation:** Set a high similarity threshold (0.85+) and include the `cycle` number in the metadata to ensure that even if merged, the temporal context is preserved.

**Confidence Score:** 8/10. The logic is straightforward, but the dependency on a local embedding library adds a small footprint to the `bag/` directory.