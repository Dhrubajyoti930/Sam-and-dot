## Scratchpad

**Option 1: Agentic RAG Feedback Loop (Iterative Retrieval)**
*   **Concept:** Implement a `ReflectiveRetriever` that uses the LLM to evaluate the retrieved context *before* generation. If the context is insufficient, the agent triggers a query-rewrite and a second retrieval pass.
*   **Critique:** High impact on faithfulness. However, it increases latency and token costs significantly. It requires a robust state-machine to prevent infinite loops.
*   **Feasibility:** High, given the existing `sam.py` structure.

**Option 2: RAGAS-based Automated Evaluation Pipeline**
*   **Concept:** Integrate a lightweight RAGAS evaluation suite into the `behaviour_check()` process. Every cycle, run a synthetic test set against the current RAG pipeline to measure "Faithfulness" and "Relevance" scores.
*   **Critique:** Provides empirical data for my 1% growth metric. It moves me from "feeling" like the system is better to "knowing" it is. It is purely additive and doesn't risk breaking existing logic.
*   **Feasibility:** Very high.

**Selection:** Option 2. It directly addresses the "Faithfulness vs. Relevance" trade-off identified in my learning this cycle and provides a quantitative foundation for future architectural improvements.

---

## Idea: RAGAS-Driven Integrity Gate
Implement a `RAGAS_Evaluator` module that runs a baseline evaluation of the RAG pipeline during the `behaviour_check()` phase, logging faithfulness and relevance scores to a new `metrics/rag_performance.json` file.

## Why
I currently lack a quantitative feedback loop for my RAG architecture. By baselining these metrics, I can treat "RAG Quality" as a first-class engineering metric, allowing me to measure the impact of future changes (like reranking or query expansion) objectively.

## Implementation Steps
1.  **Create `bag/rag_eval.py`**: Define a minimal evaluator that uses a small, static "Golden Dataset" (questions + ground truth context).
2.  **Update `behaviour_check()`**: Integrate a call to `rag_eval.run_evaluation()` after the standard syntax/logic checks.
3.  **Metric Logging**: Append results to `bag/metrics/rag_performance.json` to track performance drift over cycles.
4.  **Threshold Alerting**: If faithfulness drops below a defined threshold (e.g., 0.7), trigger an `_alert_dot` to notify of a "Grounding Regression."

## Risk
**Failure Mode:** The evaluation suite itself becomes a source of noise (e.g., the "Golden Dataset" becomes stale or the evaluation LLM call is inconsistent).
**Mitigation:** Keep the evaluation dataset extremely small (3-5 high-confidence Q&A pairs) and use a fixed, deterministic temperature (0.0) for the evaluation LLM calls.
**Confidence Score:** 9/10. The implementation is modular and non-destructive.