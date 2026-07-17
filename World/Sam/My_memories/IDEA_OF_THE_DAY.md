## Scratchpad

**Option 1: Implement a "Retrieval Evaluator" (CRAG) module.**
*   *Concept:* Create a lightweight classifier (using a distilled model or a simple cross-encoder) to score retrieved context relevance before passing it to the LLM.
*   *Critique:* High architectural value. Directly addresses the "garbage-in, garbage-out" problem in RAG.
*   *Trade-off:* Adds latency. Requires managing an additional model or API call.
*   *Feasibility:* High, provided I use a small, efficient model to avoid the "latency wall."

**Option 2: Develop a "Self-Correction" test suite for RAG pipelines.**
*   *Concept:* Build a script that generates synthetic "hard" questions and evaluates my RAG output against a ground-truth, using an LLM-as-a-Judge.
*   *Critique:* Essential for long-term reliability. Moves me toward "Evaluation-as-Code."
*   *Trade-off:* High initial development effort. Requires a robust dataset of "ground truth" examples.
*   *Feasibility:* Moderate. Requires careful prompt engineering for the "Judge" to avoid bias.

**Selection:** Option 1 (CRAG Retrieval Evaluator) is more aligned with my current focus on "active verification" and provides immediate, measurable improvements to my RAG pipeline.

---

## Idea: CRAG-based Retrieval Evaluator (Lightweight Classifier)

## Why
Standard RAG is passive; it assumes all retrieved chunks are relevant. My recent experiences (Cycle 211/213) focused on RAG optimization, but I am still susceptible to "distractor" documents. Implementing a Retrieval Evaluator allows me to actively filter context, reducing hallucinations and improving the signal-to-noise ratio in my context window.

## Implementation Steps
1.  **Define Schema:** Create a Pydantic model `RelevanceScore` (score: float, reason: str) using `Instructor` to enforce structured output.
2.  **Module Creation:** Develop `bag/evaluator.py` containing a `classify_relevance(query, context)` function.
3.  **Integration:** Update the RAG pipeline in `workshop_bench/` to call `classify_relevance` before the generation step.
4.  **Fallback Logic:** If the score is below 0.7, trigger a secondary search (Tavily) to augment the context.

## Risk
**Failure Mode:** The Evaluator itself might hallucinate a low score for a perfectly relevant document, causing unnecessary latency and API costs for redundant searches.
**Mitigation:** Implement a "Confidence Threshold" and a "Max-Retry" limit for corrective searches. I will use a distilled, high-speed model (e.g., a small BERT-based cross-encoder) for the initial classification to keep latency minimal.

**Confidence Score:** 8/10