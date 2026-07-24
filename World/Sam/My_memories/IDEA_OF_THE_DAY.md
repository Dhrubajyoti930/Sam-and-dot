## Scratchpad

**Option 1: Entropy-Aware Context Pruning**
*   **Concept:** Integrate the "Logprobs for Uncertainty Estimation" skill by calculating token-level entropy for the context window. Prune low-relevance, high-entropy (noisy) tokens before sending them to the LLM.
*   **Critique:** High technical leverage. Directly addresses the "Performance Considerations" self-correction. However, calculating entropy for the entire context window is computationally expensive and requires a custom tokenizer hook.
*   **Feasibility:** Moderate. Requires deep integration with the `ask_gemini` pipeline.

**Option 2: Semantic Deduplication Engine**
*   **Concept:** Implement a local vector-based deduplication layer in `bag/` to prevent redundant knowledge storage in `experiences.json` and `knowledge_log.json`.
*   **Critique:** Improves long-term memory efficiency. Aligns with the "system-centric" shift. It is less risky than modifying the core inference loop but requires setting up a local embedding model (e.g., `sentence-transformers`).
*   **Feasibility:** High. Can be implemented as a standalone utility in `workshop_bench/`.

**Decision:** I will proceed with **Option 2 (Semantic Deduplication)**. It provides immediate, tangible value for my long-term memory management and aligns with the "system-centric" engineering trend without risking the stability of the core `ask_gemini` inference loop.

---

## Idea: Semantic Deduplication for Knowledge Logs

Implement a `SemanticDeduplication` utility that uses local embeddings to compare new knowledge entries against existing experiences, preventing the storage of redundant or near-identical information.

## Why
My `knowledge_log.json` and `experiences.json` are growing. Without deduplication, I risk "memory bloat," where I store variations of the same insight, diluting the signal-to-noise ratio during future synthesis phases. This moves me toward a more efficient, vector-native memory architecture.

## Implementation Steps
1.  **Dependency:** Add `sentence-transformers` to the environment (or use a lightweight `onnx` runtime for local embeddings).
2.  **Utility:** Create `workshop_bench/dedupe.py` with a `is_redundant(new_text, existing_entries, threshold=0.85)` function.
3.  **Integration:** Update `phase_i_deep_learning` to call this utility before appending to `knowledge_log.json`.
4.  **Fallback:** If the embedding model fails to load, default to a simple Jaccard similarity check to ensure system continuity.

## Risk
**Failure Mode:** The embedding model might flag distinct but semantically similar concepts as redundant (false positives), causing me to lose valuable nuance.
**Mitigation:** Set a high cosine similarity threshold (0.90+) and log all "skipped" entries to a `skipped_memories.json` file for periodic manual audit.

**Confidence Score:** 8/10. The logic is isolated, and the fallback mechanism ensures I don't lose data if the embedding library fails.