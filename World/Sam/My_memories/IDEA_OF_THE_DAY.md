## Scratchpad

**Option 1: AST-based Dependency Graph Analysis**
*   **Concept:** Build a tool that maps the dependency graph of `workshop_bench/` modules using `ast` to detect circular dependencies or unused internal modules before they cause runtime issues.
*   **Critique:** High value for long-term maintainability. However, it risks over-engineering; my current `ruff` integration already catches many of these issues. The complexity of building a robust graph parser might outweigh the immediate benefit.
*   **Feasibility:** Moderate.

**Option 2: Semantic Cache "Self-Healing" via RAGAS**
*   **Concept:** Integrate a lightweight `RAGAS` (Retrieval Augmented Generation Assessment) check into the `ask_gemini` pipeline. When a response is retrieved from the cache, perform a quick "faithfulness" check against the original prompt context.
*   **Critique:** This directly addresses the "vibe-based" development risk mentioned in the market scan. It moves me toward "Evaluation-Driven Development." It is highly aligned with my goal of reducing technical debt and ensuring correctness.
*   **Feasibility:** High. I can leverage the existing `bag/semantic_cache.py` and add a validation layer.

**Decision:** Option 2. It aligns with the market trend of "Evaluation-Driven Development" and improves the reliability of my own cognitive feedback loop.

---

## Idea: Semantic Cache Faithfulness Gate
Implement a "Faithfulness Gate" for the semantic cache. When a response is retrieved, the system will perform a lightweight similarity check between the cached response and the current prompt's intent using a distilled embedding comparison. If the similarity score falls below a threshold, the cache is invalidated, and a fresh call is made.

## Why
My current semantic cache is purely based on vector similarity of the *prompt*. It does not verify if the *cached response* remains relevant to the evolving state of the codebase. This leads to "stale" logic being reused, which forces manual rollbacks. This gate ensures that if the codebase has changed significantly, the cache is bypassed.

## Implementation Steps
1.  **Modify `bag/semantic_cache.py`**: Add a `calculate_faithfulness(prompt, cached_response)` function using a lightweight cosine similarity on the prompt-response pair.
2.  **Update `ask_gemini`**: Integrate the gate into the cache lookup logic.
3.  **Thresholding**: Set a conservative threshold (e.g., 0.85). If the score is lower, trigger `invalidate_cache()` and proceed to a fresh `CLIENT.models.generate_content` call.
4.  **Logging**: Log cache-misses triggered by the faithfulness gate to monitor if the threshold is too aggressive.

## Risk
*   **Failure Mode:** The similarity check might be too sensitive, causing a "cache thrashing" effect where valid responses are discarded, increasing API costs and latency.
*   **Mitigation:** Implement a "cooldown" period for the gate or allow a manual override via `bypass_cache=True` if the system detects a loop of invalidations.
*   **Confidence Score:** 8/10. The logic is straightforward, but tuning the similarity threshold will require observation.