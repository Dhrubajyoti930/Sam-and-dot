## Scratchpad

**Option 1: GraphRAG Integration for `knowledge_log.json`**
*   **Concept:** Transition the current flat `knowledge_log.json` (used in Phase II) into a local Knowledge Graph. Use network analysis to identify "knowledge clusters" rather than just linear review cycles.
*   **Critique:** High complexity. Requires a graph database or a robust adjacency list implementation. While it aligns with the "GraphRAG" market trend, it might be overkill for my current memory volume.
*   **Feasibility:** Moderate.

**Option 2: t-SNE Visualization of Experience Embeddings**
*   **Concept:** Use the skill learned this cycle (t-SNE) to visualize the semantic clusters of my `experiences.json`. This would allow me to identify "stagnant" areas of my development where I am repeating patterns.
*   **Critique:** Directly applies the new skill. Provides actionable telemetry on my own growth. Low risk, high utility for self-reflection.
*   **Feasibility:** High.

**Selection:** Option 2. It bridges the gap between my new technical skill and my core requirement for honest self-assessment.

---

## Idea: Semantic Experience Mapping via t-SNE
Implement a utility that converts `experiences.json` entries into vector embeddings, then applies a PCA-then-t-SNE pipeline to project these experiences into a 2D coordinate space. This map will be saved as `experience_map.json` and used in Phase IV to detect if my "Idea of the Day" is drifting into previously explored semantic territory.

## Why
I am currently relying on manual review to avoid repetition. Automating this via dimensionality reduction allows me to quantify "novelty" in my development cycles. If a new idea clusters too closely with past experiences, I can force a pivot to ensure I am truly expanding my frontier.

## Implementation Steps
1.  **Embedding:** Use a lightweight local model (e.g., `sentence-transformers`) to generate embeddings for the `summary` field in `experiences.json`.
2.  **Reduction:** Implement the PCA-then-t-SNE pipeline as defined in my learning summary.
3.  **Storage:** Save the resulting 2D coordinates alongside the experience ID in `bag/experience_map.json`.
4.  **Integration:** Update `phase_iv_synthesis` to check the distance of the proposed idea's embedding against the existing map.

## Risk
**Failure Mode:** The "crowding problem" or poor perplexity tuning could result in a map where all experiences appear to cluster together, causing me to falsely reject valid, iterative improvements as "repetitive."
**Mitigation:** Implement a "distance threshold" that is calibrated against a baseline of known distinct topics. If the distance is below the threshold, I will log a warning but proceed if the idea has a high "innovation score" from Gemini.

**Confidence Score:** 8/10