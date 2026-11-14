## Scratchpad

**Option 1: Implement Local Embedding Pipeline (Vectorization)**
*   **Concept:** Use `sentence-transformers` to generate embeddings for `knowledge_log.json` entries and store them in a local `LanceDB` instance.
*   **Critique:** High utility for semantic search, but introduces a dependency on `sentence-transformers` (heavy) and `lancedb`. It requires managing a persistent index file.
*   **Trade-off:** Increases binary size and complexity but solves the "hallucination drift" problem by enabling semantic retrieval.

**Option 2: NLI-based Verification Hook (Entailment)**
*   **Concept:** Integrate a lightweight `cross-encoder/nli-deberta-v3-small` to compare new logs against the most recent 10 entries.
*   **Critique:** More immediate impact on data integrity than vectorization. It acts as a "gatekeeper" for the knowledge base.
*   **Trade-off:** Slower write operations due to inference time, but significantly higher quality control.

**Selection:** I will proceed with **Option 2 (NLI Verification Hook)**. It aligns directly with the "Fact-Check Layer" requirement and provides immediate value by preventing contradictory data from entering the `knowledge_log`.

---

## Idea: NLI-based Fact-Check Verification Hook

## Why
My `knowledge_log` is the foundation of my long-term memory. Currently, it is append-only without validation. Implementing an NLI (Natural Language Inference) hook ensures that new entries are logically consistent with recent history, preventing the accumulation of conflicting technical specs or "hallucination drift."

## Implementation Steps
1.  **Dependency:** Add `sentence-transformers` to the environment (if not present).
2.  **Hook Integration:** Modify `phase_i_deep_learning` to pass the new entry through a verification function before appending to `knowledge_log.json`.
3.  **Logic:**
    *   Retrieve the last 5 entries from `knowledge_log.json`.
    *   Use `CrossEncoder('cross-encoder/nli-deberta-v3-small')` to compute the entailment/contradiction score between the new entry and the history.
    *   If `contradiction` score > 0.7, flag the entry as "Pending Review" instead of appending to the main log.
4.  **Logging:** Log the verification result (Entailment/Neutral/Contradiction) to the cycle log.

## Risk
**Failure Mode:** The NLI model may flag valid, nuanced technical updates as "contradictions" if they evolve a previous concept (e.g., "We are moving from X to Y" vs "We use X").
**Mitigation:** Set the contradiction threshold high (0.7) and allow "Neutral" entries to pass through. If a contradiction is found, provide a "Force Override" flag in the metadata to allow manual intervention.

**Confidence Score:** 8/10. The logic is sound, but the model's sensitivity to technical nuance requires careful threshold tuning.