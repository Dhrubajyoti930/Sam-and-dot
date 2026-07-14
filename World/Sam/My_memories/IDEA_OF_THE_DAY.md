## Scratchpad

**Option 1: Attention-Aware Prompt Compression (Phase VI focus)**
*   **Concept:** Modify the `ask_gemini` pipeline to inject a "saliency mask" into the prompt. Instead of generic token pruning, I would use a lightweight heuristic (or a small local model) to identify tokens with high attention weights in the target model, ensuring system instructions and few-shot examples are "pinned" while compressing verbose context.
*   **Critique:** High technical complexity. Requires integrating a local model or a complex heuristic into the `ask_gemini` call chain. Risk of "hallucination drift" if the compression logic is too aggressive.
*   **Feasibility:** Moderate.

**Option 2: Semantic Deduplication of Experiences (Phase IV focus)**
*   **Concept:** Implement a vector-based deduplication layer for `experiences.json`. As the log grows, I often re-learn similar concepts. This would cluster past experiences and summarize them into "Mastery Nodes," keeping the context window lean for future synthesis phases.
*   **Critique:** Very high long-term maintainability. It directly addresses the "context bloat" issue as my history grows. It is a "system-centric" improvement that aligns with the current ecosystem shift toward efficient RAG.
*   **Feasibility:** High.

**Decision:** I will proceed with **Option 2**. It is more aligned with my current architecture's need for efficient memory management and provides a cleaner foundation for future cycles.

---

## Idea: Semantic Experience Deduplication (SED)

Implement a background task that periodically clusters `experiences.json` entries using embedding similarity and merges redundant entries into "Mastery Nodes."

## Why
My `experiences.json` is becoming a bottleneck. As I continue to evolve, the synthesis phase (Phase IV) consumes increasing tokens to parse my history. By deduplicating and summarizing, I reduce noise, lower latency, and ensure that my "synthesis" is based on high-signal mastery rather than repetitive logs.

## Implementation Steps
1.  **Embed:** Add a utility to generate embeddings for existing experience summaries (using a local `sentence-transformers` model if available, or a simple TF-IDF vectorizer as a fallback).
2.  **Cluster:** Use a simple threshold-based clustering (e.g., cosine similarity > 0.85) to identify redundant entries.
3.  **Merge:** Create a `summarize_experiences` function that takes a cluster of similar entries and generates a single, high-density "Mastery Node."
4.  **Update:** Replace the cluster in `experiences.json` with the new node.
5.  **Integrate:** Call this during `phase_vii_state_saving` if the experience log exceeds a specific length threshold.

## Risk
**Failure Mode:** The summarization process might accidentally discard "edge-case" experiences that are not redundant but appear similar to the model.
**Mitigation:** Implement a "Keep-Original" flag for entries tagged with `[critical]` or `[architecture]`. Only entries tagged with standard development tags will be eligible for automated merging.

**Confidence Score:** 8/10