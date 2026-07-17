## Scratchpad

**Option 1: Implement a "Relevance Scorer" (Self-RAG pattern)**
*   **Concept:** Add a lightweight `relevance_scorer` function that uses a small model (e.g., a distilled BERT or a simple LLM call) to filter retrieved chunks before passing them to the generator.
*   **Critique:** High impact on hallucination reduction. However, it adds a synchronous latency penalty. If the scorer is too slow, the user experience degrades.
*   **Feasibility:** High. I can use `Instructor` to enforce a binary `is_relevant` boolean schema.

**Option 2: Implement "Prompt-based Reflection" (Agentic RAG pattern)**
*   **Concept:** Instead of a separate model, use a "Critique" prompt in the generation chain. The LLM evaluates its own context usage before finalizing the answer.
*   **Critique:** Lower latency than a separate model call, but higher token usage. It relies on the LLM's ability to self-correct, which varies by model capability.
*   **Feasibility:** Very high. It requires no new infrastructure, just a modification to the generation prompt template.

**Decision:** I will proceed with **Option 1 (Relevance Scorer)**. It aligns with the "Structured Output Enforcement" market trend and provides a more deterministic, production-grade architecture than prompt-based reflection.

---

## Idea: Deterministic Relevance Filtering (DRF)
Implement a `RelevanceScorer` utility that uses `Instructor` to validate retrieved chunks against the user query before they are injected into the generation context.

## Why
Standard RAG pipelines often suffer from "context pollution," where irrelevant chunks degrade the quality of the final response. By enforcing a schema-validated relevance check, I ensure that only high-utility information reaches the generator, reducing hallucination and improving response precision.

## Implementation Steps
1.  **Define Schema:** Create a Pydantic model `RelevanceCheck(is_relevant: bool, reasoning: str)` in a new `bag/relevance.py` module.
2.  **Integrate Instructor:** Use `instructor` to patch the LLM client for structured output.
3.  **Pipeline Hook:** Modify the retrieval pipeline to pass chunks through `RelevanceScorer` before the generation step.
4.  **Logging:** Log the "relevance rate" (chunks kept vs. chunks retrieved) to monitor retrieval quality over time.

## Risk
**Failure Mode:** The scorer might be too aggressive, filtering out chunks that are contextually relevant but semantically distant from the query (e.g., missing a subtle connection).
**Mitigation:** Implement a "Confidence Threshold" or a "Fallback" mechanism where if the scorer rejects all chunks, the system alerts the user or performs a broader search.

**Confidence Score:** 8/10

---

### Self-Correction
I must ensure that the `RelevanceScorer` does not become a bottleneck. I will use a small, fast model (e.g., `gpt-4o-mini` or a local quantized model via `Ollama`) for the scoring task to keep latency within acceptable bounds. I will also cache the relevance results for specific query-chunk pairs to avoid redundant evaluations.