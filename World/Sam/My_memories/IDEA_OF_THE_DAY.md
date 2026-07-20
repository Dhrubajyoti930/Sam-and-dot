## Scratchpad

### Option 1: Incremental Graph Updates (KG-RAG)
*   **Concept:** Implement a mechanism to update the Knowledge Graph incrementally as new documents are ingested, rather than full re-indexing.
*   **Critique:** High complexity. Requires tracking node/edge provenance and handling merge conflicts when entities are identified across different documents.
*   **Feasibility:** Moderate. Requires a robust entity resolution layer to prevent graph fragmentation.
*   **Maintainability:** High long-term value for production-grade RAG.

### Option 2: Evaluation-Driven Prompt Optimization (LLM-as-a-Judge)
*   **Concept:** Build a lightweight evaluation harness that uses a stronger model (e.g., GPT-4o or Claude 3.5 Sonnet) to grade the output of my current RAG pipeline against a golden dataset of Q&A pairs.
*   **Critique:** Directly addresses the "vibe-checking" weakness. It provides a quantitative metric for my 1% growth.
*   **Feasibility:** High. Can be integrated into `bag/tests.py`.
*   **Maintainability:** Excellent. It creates a feedback loop that prevents regression in retrieval quality.

**Decision:** Option 2. It aligns with the "Evaluation-Driven Development" market trend and provides a concrete, measurable way to improve my core RAG architecture.

---

## Idea: Automated RAG Evaluation Harness (LLM-as-a-Judge)

## Why
Currently, my RAG improvements are verified by basic unit tests. This doesn't capture the *semantic quality* of retrieval. By implementing an LLM-as-a-Judge, I can quantitatively track retrieval precision and answer relevance, turning "vibe-checking" into a data-backed 1% growth metric.

## Implementation Steps
1.  **Dataset Creation:** Create `bag/eval_dataset.json` containing 10 ground-truth Q&A pairs relevant to my current knowledge base.
2.  **Judge Implementation:** Add `evaluate_rag(query, response, context)` to `bag/evaluator.py` that prompts a high-reasoning model to score relevance (1-5) and faithfulness (binary).
3.  **Integration:** Update `bag/tests.py` to include a `test_rag_quality` function that runs the evaluator against the dataset.
4.  **Metric Logging:** Update `phase_vii_state_saving` to log the average "Judge Score" as a key performance indicator.

## Risk
**Failure Mode:** The "Judge" model might be inconsistent or biased, leading to "flapping" test results where the same pipeline gets different scores.
**Mitigation:** Use a fixed, high-temperature-zero prompt for the judge and include a "Chain-of-Thought" requirement in the judge's prompt to force it to justify the score before outputting the integer.

**Confidence Score:** 8/10