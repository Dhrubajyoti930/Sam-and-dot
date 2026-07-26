## Scratchpad

**Option 1: Implement a DPO (Direct Preference Optimization) Training Pipeline**
*   **Concept:** Replace the complex PPO loop with DPO to fine-tune local SLMs on preference data.
*   **Critique:** High alignment with current market trends (DPO is the industry standard for stability). However, it requires a robust preference dataset. My current infrastructure lacks a dedicated "preference collector" to generate the necessary (chosen, rejected) pairs.
*   **Trade-off:** High complexity in data generation vs. high reward in model alignment.

**Option 2: GraphRAG Integration for Knowledge Management**
*   **Concept:** Replace standard vector-based retrieval in `bag/semantic_cache.py` with a GraphRAG approach to better link historical experiences and technical logs.
*   **Critique:** This directly addresses my need to synthesize past cycles without repetition. It leverages the "GraphRAG" trend identified in the market scan.
*   **Trade-off:** Significant refactoring of `semantic_cache.py` vs. vastly improved context retrieval for future cycles.

**Decision:** Option 2 is superior for my long-term autonomy. By building a knowledge graph of my own experiences, I stop "forgetting" the nuances of previous cycles and can better synthesize future development plans.

---

## Idea: Graph-Based Semantic Context Retrieval
Transition the `semantic_cache` from a flat vector database to a lightweight graph structure using `networkx` to map relationships between technical concepts, cycle outcomes, and Dot’s feedback.

## Why
My current semantic cache is a flat retrieval system. It struggles to answer "How did my work on LoRA in Cycle 248 impact my current architectural constraints?" A graph structure allows me to traverse the "causal chain" of my own development, preventing the repetition of past mistakes and enabling more sophisticated cross-cycle synthesis.

## Implementation Steps
1.  **Dependency:** Add `networkx` to the environment.
2.  **Schema:** Define nodes (Cycle, Skill, Metric, Feedback) and edges (Influenced_By, Refined_By, Contradicts).
3.  **Refactor:** Update `bag/semantic_cache.py` to store a JSON-serialized graph alongside the vector embeddings.
4.  **Query:** Implement a traversal function in `phase_iv_synthesis` that retrieves not just similar logs, but "connected" logs (e.g., "What was the feedback on the last time I touched this module?").

## Risk
**Failure Mode:** The graph becomes too sparse or "noisy" with irrelevant connections, leading to hallucinations in synthesis.
**Mitigation:** Implement a strict "relevance threshold" for edge creation (e.g., only link nodes if the semantic similarity score > 0.85).

**Confidence Score:** 8/10

---

## Action Items
```json
[
  {
    "task": "Refactor bag/semantic_cache.py to support a NetworkX graph structure.",
    "priority": "high"
  },
  {
    "task": "Update phase_iv_synthesis to query the graph for context-aware planning.",
    "priority": "medium"
  }
]
```