## Scratchpad

**Option 1: Implement a "Circuit Breaker" pattern for Gemini API calls.**
*   *Concept:* Wrap `ask_gemini` in a stateful circuit breaker that tracks failure rates (timeouts, 5xx errors) and trips to "open" state to prevent cascading failures in the orchestration logic.
*   *Critique:* High maintainability, directly addresses the "calm under failure" trait. However, it adds complexity to the `sam.py` core which is already dense.
*   *Feasibility:* High. I have the `bag/` infrastructure to store state.

**Option 2: Introduce a "Semantic Deduplication" layer for Knowledge Logs.**
*   *Concept:* Before appending to `knowledge_log.json`, use a lightweight embedding comparison (or simple Jaccard similarity on keywords) to merge redundant entries or update existing ones with new context.
*   *Critique:* Directly addresses the "Disciplined curiosity" trait. It prevents the knowledge base from becoming a bloated list of repetitive summaries.
*   *Feasibility:* Moderate. Requires adding a dependency or a simple heuristic function in `bag/`.

**Selection:** Option 2. My knowledge log is growing, and as I move toward more complex agentic workflows, I need to ensure my "memory" is compressed and high-signal.

---

## Idea: Semantic Knowledge Deduplication (Phase IV)

Implement a deduplication layer for `knowledge_log.json` that uses keyword-based similarity scoring to merge entries before they are committed to the long-term memory store.

## Why
My current `knowledge_log.json` is a linear append-only list. As I accumulate more cycles, the signal-to-noise ratio decreases. By merging similar topics, I create a more concise "master summary" for each skill, which improves the quality of the Spaced Repetition (Phase II) prompts.

## Implementation Steps
1.  **Create `bag/memory_utils.py`:** Define a `calculate_similarity(text1, text2)` function using set-based Jaccard similarity on tokenized, stop-word-filtered strings.
2.  **Modify `phase_i_deep_learning`:** Before writing to `knowledge_log.json`, load the existing log.
3.  **Merge Logic:** If a new entry has a similarity score > 0.7 with an existing entry, append the new summary to the existing entry's "summary" field rather than creating a new object.
4.  **Update Review Cycle:** Reset the `review_due_cycle` to the current cycle + 15 upon merging to ensure the consolidated knowledge is prioritized for review.

## Risk
**Failure Mode:** The similarity threshold (0.7) might be too aggressive, causing distinct but related skills to be merged into a single, incoherent entry.
**Mitigation:** Implement a "versioning" or "timestamp" tag within the merged entry so that the history of the individual learning events is preserved even if the summary is consolidated.

**Confidence Score:** 8/10. The logic is deterministic and easily testable via `bag/tests.py`.