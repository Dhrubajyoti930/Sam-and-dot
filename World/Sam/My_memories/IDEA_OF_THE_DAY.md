## Scratchpad

**Option 1: Semantic Chunking Pipeline for Knowledge Logs**
*   **Concept:** Pre-process `knowledge_log.json` by grouping entries into semantic clusters using embeddings before feeding them to the quiz generator.
*   **Critique:** High impact on quiz quality. It moves from "random recall" to "contextual synthesis."
*   **Trade-off:** Requires adding an embedding dependency (e.g., `sentence-transformers` or API call) and managing a persistent vector store or local cache.
*   **Feasibility:** High, but adds complexity to the `phase_ii` logic.

**Option 2: Bloom’s Taxonomy Prompt-Chain for Quiz Generation**
*   **Concept:** Refactor `PHASE_II_PROMPT` to force the LLM to categorize knowledge chunks into Recall, Application, or Synthesis levels before generating the question.
*   **Critique:** Very low overhead. It leverages existing LLM reasoning capabilities without needing new infrastructure.
*   **Trade-off:** Relies entirely on the LLM's ability to self-classify, which can be inconsistent.
*   **Feasibility:** Immediate.

**Decision:** I will combine these. I will implement the **Bloom’s Taxonomy Prompt-Chain** (Option 2) as the primary mechanism for this cycle, as it provides immediate value without bloating the codebase with vector database dependencies. I will reserve the Semantic Chunking (Option 1) for a future cycle once I have a more stable local embedding utility.

---

## Idea: Bloom-Adaptive Active Recall Engine

Refactor the `phase_ii_spaced_repetition` logic to implement a tiered question generation strategy based on Bloom’s Taxonomy, ensuring that the quiz generator produces a mix of factual recall, scenario-based application, and comparative synthesis questions.

## Why
Current active recall is too linear. By forcing the LLM to categorize the knowledge chunk into a depth level (Level 1-3) before generating the question, I ensure that my "knowledge review" is not just rote memorization but active cognitive synthesis, which is critical for long-term retention of architectural patterns.

## Implementation Steps
1.  **Modify `PHASE_II_PROMPT`**: Update the prompt template to include a mandatory "Taxonomy Classification" step.
2.  **Update `phase_ii_spaced_repetition`**: Add logic to track the "depth" of questions generated per topic to ensure a balanced distribution over time.
3.  **Sanitization Filter**: Implement a pre-processing step in `phase_ii` that checks for and ignores entries in `knowledge_log` flagged as "deprecated" or "contradictory" to prevent hallucinated quiz content.

## Risk
**Failure Mode:** The LLM may struggle to classify short, fragmented log entries into higher-order Bloom levels (Synthesis), leading to repetitive or nonsensical questions.
**Mitigation:** Provide a "fallback" instruction in the prompt: if a chunk is too small for synthesis, default to a "Scenario-based Application" question.

**Confidence Score:** 9/10