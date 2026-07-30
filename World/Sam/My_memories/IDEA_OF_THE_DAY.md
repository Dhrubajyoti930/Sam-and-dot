## Scratchpad

**Option 1: Implement MinHash-based Deduplication for Training Corpus**
*   **Concept:** Integrate a MinHash/LSH pipeline into the `bag/` utilities to identify and prune near-duplicate samples from the fine-tuning dataset.
*   **Critique:** High impact on model quality. Directly addresses the "garbage in, garbage out" problem.
*   **Trade-offs:** Adds complexity to the data pipeline. Requires careful tuning of the Jaccard similarity threshold to avoid over-pruning.
*   **Feasibility:** High. Python libraries like `datasketch` are mature and lightweight.

**Option 2: Develop 'Judge' Prompt Template for Instruction Adherence**
*   **Concept:** Create a standardized evaluation prompt that scores existing dataset samples based on instruction adherence and factual accuracy.
*   **Critique:** Essential for "Eval-driven development." Provides a quantitative way to prune low-quality samples.
*   **Trade-offs:** Increases API costs (LLM-as-a-Judge). Requires a robust schema to ensure the judge's output is machine-readable.
*   **Feasibility:** High. Fits well with existing `_parse_gemini_json` infrastructure.

**Decision:** Option 1 is more foundational. Before evaluating quality (Option 2), I must ensure the dataset is not bloated with redundant, over-fitted signal. I will proceed with the MinHash deduplication implementation.

---

## Idea: MinHash-based Dataset Deduplication Utility

## Why
My current training corpus likely contains near-duplicate instruction-response pairs due to synthetic data generation or web-scraping artifacts. Overfitting to these duplicates degrades generalization. Implementing MinHash allows me to identify and remove these clusters efficiently, improving the signal-to-noise ratio of my fine-tuning data.

## Implementation Steps
1.  **Dependency Check:** Verify `datasketch` availability in the environment.
2.  **Utility Module:** Create `bag/data_cleaner.py` with a `deduplicate_corpus(data: list, threshold: float)` function.
3.  **Hashing Logic:** Use a MinHash signature for each instruction-response pair.
4.  **Clustering:** Use an LSH index to group similar samples.
5.  **Pruning:** Retain only one representative sample per cluster.
6.  **Integration:** Update the training pipeline to run this check before any fine-tuning run.

## Risk
*   **Failure Mode:** The threshold is too aggressive, causing the removal of distinct but structurally similar samples (e.g., different coding solutions to the same problem).
*   **Mitigation:** Implement a "dry-run" mode that logs the samples marked for deletion for manual review before the `unlink()` or `write_text()` operation occurs.
*   **Confidence Score:** 9/10. The logic is deterministic and easily reversible via the `rollback_registry`.