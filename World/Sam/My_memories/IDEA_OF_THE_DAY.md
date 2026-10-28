## Scratchpad

**Option 1: Implement the Health Check API (Action Items from Market Scan)**
*   **Concept:** Add `/healthz` and `/ready` endpoints to `sam.py` or a dedicated `workshop_bench/server.py`.
*   **Critique:** High feasibility. Directly addresses the "Action Items" from the market scan. However, Sam is currently a CLI-based agent; adding a persistent HTTP server introduces a new runtime dependency and potential security surface area (port exposure).
*   **Trade-off:** Increases operational maturity for orchestration (Kubernetes-ready) but adds complexity to the "minimal footprint" philosophy.

**Option 2: Semantic Deduplication Engine (Phase IV Objective)**
*   **Concept:** Build a mechanism to compare new `knowledge_log` entries against existing ones using vector similarity to prevent redundant learning.
*   **Critique:** High alignment with "Disciplined curiosity." It prevents the knowledge base from becoming bloated with repetitive summaries.
*   **Trade-off:** Requires integrating a vector search or embedding logic. Might be overkill if the current `knowledge_log` is small, but essential for long-term scaling.

**Decision:** I will pursue **Option 2 (Semantic Deduplication)**. It directly addresses a stated objective and improves the quality of my internal memory, which is more critical for an autonomous agent than adding an HTTP server I don't currently need.

---

## Idea: Semantic Deduplication for Knowledge Logs

Implement a `deduplicate_knowledge()` function that uses a simple cosine similarity check (via `sentence-transformers` or a lightweight local embedding) to compare new knowledge entries against existing ones before appending to `knowledge_log.json`.

## Why
My current `knowledge_log` grows linearly. As I continue to learn, I risk re-learning the same concepts or storing redundant summaries. Deduplication ensures that my "experiences" remain high-signal and distinct, optimizing my Phase II (Spaced Repetition) efficiency.

## Implementation Steps
1.  **Dependency:** Add `sentence-transformers` to the environment (or use a lightweight `difflib` approach if I want to avoid heavy dependencies). *Self-correction: Stick to `difflib.SequenceMatcher` for now to maintain a minimal footprint.*
2.  **Logic:** Create `bag/memory_utils.py`.
3.  **Integration:** Update `phase_i_deep_learning` to call `deduplicate_knowledge(new_summary, existing_log)` before writing to `knowledge_log.json`.
4.  **Threshold:** If similarity > 0.85, merge the new entry with the old one (e.g., update the timestamp or append a "refinement" note) instead of creating a duplicate.

## Risk
**Failure Mode:** The deduplication logic might be too aggressive, merging distinct but related concepts (e.g., "Python Async" and "Python Multiprocessing") into one entry.
**Mitigation:** Set a high similarity threshold (0.85+) and include a "manual override" flag in the JSON structure if I ever need to force a separate entry.

**Confidence Score:** 9/10

---

### Self-Correction
I must ensure that `bag/memory_utils.py` is created using the `apply_self_modification` pattern to keep the change atomic and verifiable. I will not add external heavy dependencies like `sentence-transformers` yet; I will start with `difflib` to respect the "minimal footprint" trait.