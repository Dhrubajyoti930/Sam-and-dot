## Scratchpad

**Option 1: Distilled Judge Implementation**
*   **Concept:** Train a smaller, local model (e.g., Qwen2.5-7B-Instruct) to act as a "Distilled Judge" by distilling the scoring patterns of GPT-4o from the previous cycle's evaluation data.
*   **Critique:** High technical overhead. Requires setting up a training pipeline (LoRA/QLoRA). While it solves the cost/latency issue of LLM-as-a-Judge, it introduces a new dependency on local model management.
*   **Feasibility:** Moderate. Requires `llama.cpp` or `unsloth` integration.

**Option 2: Semantic Deduplication Engine**
*   **Concept:** Implement a module that computes embedding-based similarity for incoming knowledge/experiences to prevent redundant storage in `knowledge_log.json` and `experiences.json`.
*   **Critique:** Directly addresses the "minimal footprint" trait. It prevents the knowledge base from becoming a bloated echo chamber. It is a surgical, high-leverage refactor.
*   **Feasibility:** High. Uses existing vector search capabilities (Qdrant/local FAISS) and fits well within the current `bag/` architecture.

**Selection:** Option 2. It aligns with the "Semantic Deduplication" objective in `load_goals()` and directly improves the quality of the long-term memory Sam relies on for self-improvement.

---

## Idea: Semantic Deduplication Engine (SDE)

Implement a `SemanticDeduplication` class in `bag/dedupe.py` that intercepts new entries to `knowledge_log.json` and `experiences.json`, checking for high-cosine-similarity matches against existing entries before appending.

## Why
My memory is growing. Without deduplication, I risk "knowledge drift" where I re-learn the same concepts with slight variations, wasting cycles and polluting my context window. This ensures that my `knowledge_log` remains a high-density repository of unique, high-value insights.

## Implementation Steps
1.  **Create `bag/dedupe.py`**: Define `SemanticDeduplication` with a method `is_redundant(new_entry_text: str, threshold: float = 0.85)`.
2.  **Embedding Integration**: Use a lightweight local encoder (e.g., `sentence-transformers/all-MiniLM-L6-v2`) to generate vectors.
3.  **Update `phase_i_deep_learning`**: Modify the function to call `SDE.is_redundant()` before appending to `knowledge_log.json`.
4.  **Threshold Calibration**: Set the initial threshold at 0.85; adjust based on false-positive rates in the first 3 cycles.

## Risk
**Failure Mode:** The embedding model might flag distinct but conceptually related topics as "redundant" (e.g., confusing "RAG evaluation" with "RAG retrieval"), causing me to skip learning new nuances.
**Mitigation:** Implement a "Soft-Reject" log. If an entry is flagged as redundant, store it in a `redundant_log.json` instead of discarding it. I can review this log during Phase II to verify if the deduplication was too aggressive.

**Confidence Score:** 9/10