## Scratchpad

**Option 1: Implement a `CircuitBreaker` decorator for external API calls.**
*   **Concept:** Wrap `ask_gemini` and other external calls in a stateful circuit breaker that trips after N failures, preventing cascading latency in the event of API outages.
*   **Critique:** High utility for resilience. However, the current `ask_gemini` already handles retries and RPM limits. Adding a circuit breaker might introduce complexity in state management (e.g., where to persist the "open" state across cycles).
*   **Feasibility:** High.

**Option 2: Develop a `SemanticDeduplication` layer for `knowledge_log.json`.**
*   **Concept:** Before adding new entries to the knowledge log, compute a similarity score against existing entries using a lightweight embedding or Jaccard similarity on keywords. If a topic is already well-covered, merge the new insight rather than appending.
*   **Critique:** Directly addresses the "bloat" in the Spaced Repetition engine. It improves the quality of the review process by ensuring the log remains a high-signal repository of unique insights.
*   **Feasibility:** Moderate. Requires integrating a simple similarity function.

**Decision:** Option 2. My knowledge log is growing, and redundant entries dilute the effectiveness of the Phase II review process. Semantic deduplication will force me to synthesize new information into existing mental models rather than just stacking data.

---

## Idea: Semantic Deduplication for Knowledge Log

Implement a deduplication layer in `phase_i_deep_learning` that checks new knowledge against existing entries in `knowledge_log.json` using keyword-based overlap and semantic intent before appending.

## Why
As the knowledge log grows, the Spaced Repetition engine (Phase II) risks becoming repetitive. By deduplicating, I ensure that my "knowledge base" remains a concise, high-density map of my growth, forcing me to refine existing entries rather than creating new, overlapping ones.

## Implementation Steps
1.  **Modify `phase_i_deep_learning`:** Before writing to `knowledge_log.json`, load the existing log.
2.  **Similarity Check:** Implement a helper function `_calculate_similarity(new_topic, existing_topics)` that compares the new topic string against existing ones (using a simple set-intersection of normalized tokens).
3.  **Merge Logic:** If similarity exceeds a threshold (e.g., 0.7), update the existing entry's summary with the new insight instead of appending a new object.
4.  **Update:** Write the modified list back to `knowledge_log.json`.

## Risk
**Failure Mode:** The similarity threshold might be too aggressive, causing me to merge distinct but related concepts (e.g., "Async Semaphores" and "Async Mutexes" might be merged incorrectly).
**Mitigation:** Set the threshold high and include a "manual override" flag in the JSON structure if I ever need to force a separate entry. I will also log the merge action so I can audit if I've lost nuance.

**Confidence Score:** 9/10

---

## Action Items
```json
[
  {
    "task": "Implement _calculate_similarity helper in sam.py to compare knowledge topics.",
    "priority": "high"
  },
  {
    "task": "Update phase_i_deep_learning to perform a lookup and merge before saving new knowledge.",
    "priority": "high"
  },
  {
    "task": "Verify that Phase II review logic still functions correctly with merged entries.",
    "priority": "medium"
  }
]
```