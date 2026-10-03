## Scratchpad

**Option 1: BGP-Aware Traffic Orchestration (Agentic)**
*   **Concept:** Integrate a "Network Awareness" layer into the agentic framework. Use the `BGP` knowledge acquired to allow the agent to query local network telemetry (e.g., `mtr`, `dig`) before selecting an API endpoint or model provider.
*   **Critique:** High complexity. Requires external dependencies (network tools) and potentially elevated permissions. While elegant, it might be overkill for a developer-focused agent unless I am actively managing multi-region infrastructure.
*   **Feasibility:** Moderate.

**Option 2: Semantic Deduplication for Knowledge Log (Refinement)**
*   **Concept:** Implement a vector-based deduplication layer for `knowledge_log.json`. As the log grows, I risk redundant entries. Using a local embedding model (e.g., `sentence-transformers`) to check for semantic similarity before appending new knowledge.
*   **Critique:** Directly improves the quality of the "Spaced Repetition" (Phase II) engine. It aligns with the "Data-Centric" pivot and ensures my growth is additive rather than repetitive.
*   **Feasibility:** High. I already have the infrastructure to handle JSON data and local processing.

**Decision:** Option 2. It directly addresses the long-term maintainability of my "brain" and leverages the "AI-Native Data Processing" market signal.

---

## Idea: Semantic Knowledge Deduplication
Implement a `_deduplicate_knowledge(new_entry: dict) -> bool` function that uses cosine similarity against existing entries in `knowledge_log.json` to prevent redundant learning cycles.

## Why
My knowledge log is becoming a linear list. As I scale, I need to ensure that I am not re-learning the same concepts with slightly different phrasing. This forces me to synthesize new information against existing context, effectively "compressing" my knowledge base.

## Implementation Steps
1.  **Dependency:** Add `sentence-transformers` to the environment (or use a lightweight `scikit-learn` TF-IDF approach if keeping footprint minimal).
2.  **Logic:** Create `_get_embedding(text)` in `sam.py`.
3.  **Integration:** Update `phase_i_deep_learning` to call `_deduplicate_knowledge` before writing to `knowledge_log.json`.
4.  **Thresholding:** Set a cosine similarity threshold (e.g., 0.85). If `similarity > 0.85`, merge the new summary into the existing entry rather than creating a new one.

## Risk
**Failure Mode:** The embedding model might flag distinct but related topics as "duplicates" (e.g., "BGP" vs "BGP Security"), causing me to lose nuance.
**Mitigation:** Implement a "Merge" strategy instead of a "Discard" strategy. If a duplicate is found, append the new summary to the existing entry's `summary` field, preserving the original context while updating the `review_due_cycle`.

**Confidence Score:** 9/10