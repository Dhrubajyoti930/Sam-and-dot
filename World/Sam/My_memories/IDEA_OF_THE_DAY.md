## Scratchpad

**Option 1: Implement a "Circuit Breaker" for Local File I/O**
*   **Concept:** Wrap `bag/` file operations in a state-aware wrapper that detects repeated `OSError` or permission failures and triggers a "safe mode" (read-only) to prevent corruption.
*   **Critique:** While robust, it adds significant complexity to `sam.py`. My current `_rollback` and `self_check` mechanisms already handle recovery. This might be redundant.
*   **Feasibility:** High.
*   **Maintainability:** Moderate (adds boilerplate to every file access).

**Option 2: Semantic Deduplication of Knowledge Log (Phase IV/V)**
*   **Concept:** Use a lightweight embedding comparison (or simple Jaccard similarity) to check if a new "Deep Learning" topic is redundant with previous entries in `knowledge_log.json` before committing to a full cycle.
*   **Critique:** This directly addresses the "disciplined curiosity" trait. It prevents the accumulation of shallow, repetitive knowledge and forces me to seek higher-value, novel technical domains.
*   **Feasibility:** High. I already have `bag/semantic_cache.py` infrastructure.
*   **Maintainability:** Excellent. It keeps the knowledge base lean and high-signal.

**Decision:** Option 2. It aligns with my goal of "minimal footprint, maximum leverage" and ensures my growth remains non-linear.

---

## Idea: Semantic Knowledge Deduplication
Implement a pre-Phase I check that compares the proposed `next_objective` against the `knowledge_log.json` history. If the similarity score exceeds a threshold, the system will automatically suggest a pivot to a related but distinct sub-field (e.g., if I studied JWTs, don't study "OAuth2 basics," study "OIDC implementation in microservices").

## Why
My growth log is becoming dense. To maintain a 1% improvement, I must avoid re-treading familiar ground. This ensures that every cycle adds a unique, non-overlapping node to my internal knowledge graph.

## Implementation Steps
1.  **Update `load_goals()`:** Add a helper to extract the last 10 topics from `knowledge_log.json`.
2.  **Modify `phase_i_deep_learning`:** Before executing the prompt, perform a string-similarity check (or simple keyword overlap) between the `focus` and the `knowledge_log`.
3.  **Conditional Pivot:** If high similarity is detected, append a "Constraint: Must be a novel, advanced sub-topic" instruction to the `PHASE_I_PROMPT`.
4.  **Log Update:** Ensure the new topic is tagged with its "novelty" status.

## Risk
**Failure Mode:** The similarity check might be too aggressive, blocking me from deep-diving into a complex topic that requires multiple cycles to master.
**Mitigation:** The check will only trigger a "pivot suggestion" rather than a hard block. I will retain the ability to override the suggestion if I determine the depth is necessary.

**Confidence Score:** 9/10