## Scratchpad

**Option 1: Vector-based Semantic Deduplication**
*   *Concept:* Integrate `sentence-transformers` to embed objectives and compare against `knowledge_log`.
*   *Critique:* High accuracy, but introduces a heavy dependency (`torch`/`transformers`) into the `bag/` environment. This violates the "minimal footprint" principle.
*   *Feasibility:* Moderate. Requires managing a local model or an API call for embeddings.

**Option 2: Keyword-Frequency & Metadata-Aware Objective Filtering**
*   *Concept:* Enhance `load_goals` to filter `next_objectives` by checking against `knowledge_log` using Jaccard similarity on keyword sets and status-based filtering (ignoring `success` tags).
*   *Critique:* Extremely lightweight, zero external dependencies, and aligns perfectly with the current `sam.py` architecture. It leverages the existing `knowledge_log` structure.
*   *Feasibility:* High. Can be implemented as a pure Python utility within `sam.py`.

**Decision:** Option 2. It respects the "minimal footprint" constraint while providing the requested "Semantic Deduplication" functionality via a robust heuristic approach.

---

## Idea
**Implementation of a Metadata-Aware Objective Filter (MAOF)**

## Why
The current objective generator is prone to "looping behavior" where it re-proposes tasks that have already been marked as `success` or `failure` in the `knowledge_log`. By filtering the `next_objectives` list against the `knowledge_log` using status-based exclusion and keyword-frequency analysis, I can prune redundant tasks before they reach the execution phase.

## Implementation Steps
1.  **Modify `load_goals`:** Add a post-processing step that reads `knowledge_log.json`.
2.  **Status Filtering:** Identify all objectives in the `knowledge_log` with `status: "success"`.
3.  **Keyword Pruning:** For each `next_objective`, calculate a keyword overlap score against the `success` entries. If the overlap exceeds a threshold (e.g., 2+ shared technical terms), discard the objective.
4.  **Negative Constraint Injection:** Update the `phase_iv_synthesis` prompt to explicitly include the last 5 `knowledge_log` entries as "Forbidden Paths" to ensure the LLM doesn't re-generate the pruned objectives.

## Risk
*   **Failure Mode:** Over-aggressive filtering might discard a valid "re-attempt" on a task that was previously marked `inconclusive` but is now necessary due to a change in the environment.
*   **Mitigation:** Only filter objectives that are strictly marked as `success`. Keep `inconclusive` or `failure` entries in the pool, but pass them to the LLM with the `knowledge_log` context so it can adjust its strategy.
*   **Confidence Score:** 9/10.

---

### Action Items
*   [ ] Refactor `load_goals` to perform the metadata-aware filter.
*   [ ] Update `phase_iv_synthesis` prompt template to ingest `knowledge_log` context.
*   [ ] Add `status` and `tags` fields to `knowledge_log` entries during `phase_i_deep_learning`.