## Scratchpad

**Option 1: Implement the Novelty Scoring Vector Store (as per Action Items)**
*   **Concept:** Create a JSONL-based vector store of past architectural summaries. Before proposing new ideas, calculate cosine similarity to ensure the idea is "novel."
*   **Critique:** High alignment with the current cycle's learning. It directly addresses the risk of iterative stagnation. However, it adds latency to the `phase_iv_synthesis` loop and requires managing a new persistent file (`bag/novelty_index.jsonl`).
*   **Feasibility:** High. Python's `math` or `numpy` (if available) can handle cosine similarity. If external libs are restricted, a simple dot-product on normalized vectors suffices.

**Option 2: Utility-Weighted Novelty Refinement**
*   **Concept:** Instead of just checking for novelty, weight the score by the "success-factor" of past ideas (e.g., did the idea lead to a successful `self_check`?).
*   **Critique:** This is more sophisticated but significantly more complex to implement. It requires tracking "success" metrics for every past idea, which might over-engineer the current state.
*   **Feasibility:** Moderate. Requires adding a `success_score` field to the `experiences.json` and the novelty index.

**Decision:** I will proceed with **Option 1**, but integrate the "Utility-Weighted" logic as a secondary metadata field in the index to satisfy the refinement requirement without over-complicating the initial implementation.

---

## Idea: Semantic Novelty Guardrail (SNG)
Implement a lightweight vector-based novelty check that intercepts `phase_iv_synthesis`. It will compare the proposed architectural direction against a persistent `bag/novelty_index.jsonl` to ensure I am exploring new solution spaces rather than repeating past patterns.

## Why
My current synthesis relies on recent experiences, but it lacks a formal mechanism to prevent "semantic drift" or repetitive architectural patterns. By quantifying the distance between my current proposal and historical successes, I ensure that my growth remains expansive rather than circular.

## Implementation Steps
1.  **Create `bag/novelty_engine.py`:** Define a class to handle embedding generation (using a simple local tokenizer/embedding approach) and cosine similarity calculations.
2.  **Initialize `bag/novelty_index.jsonl`:** Store `{"id": int, "embedding": list, "summary": str, "utility": float}`.
3.  **Update `phase_iv_synthesis`:** 
    *   Generate an embedding for the proposed idea.
    *   Query the index for the top-k most similar past ideas.
    *   If similarity > `NOVELTY_THRESHOLD` (0.85), trigger a re-prompt to force divergence.
4.  **Log Success:** After a successful `self_check`, append the new idea to the index with a utility score based on the `self_check` result.

## Risk
**Failure Mode:** The "Semantic Drift" problem—where an idea is syntactically different but semantically identical to a previous one, causing the guardrail to trigger false positives or negatives.
**Mitigation:** Use a "Utility-Weighted" threshold. If an idea is similar to a *highly successful* past idea, I will allow it (exploitation). If it is similar to a *failed* idea, I will strictly block it.

**Confidence Score:** 8/10. The logic is sound, but the quality of the "embedding" (without heavy external libraries) will rely on a simple token-frequency vector, which is less precise than a transformer-based embedding. I will accept this trade-off for system stability.