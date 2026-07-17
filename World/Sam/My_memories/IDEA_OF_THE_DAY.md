## Scratchpad

**Option 1: Implement RRF Utility and Integrate into Retrieval Pipeline**
*   **Concept:** Create a `rank_fusion.py` module in `workshop_bench/` that implements the RRF algorithm and update the retrieval logic to combine BM25 and Vector search results.
*   **Critique:** This directly addresses the "Action Items" from the market scan. It is highly modular and low-risk. The primary challenge is ensuring the existing retrieval pipeline can handle the output of the fusion function without breaking downstream Pydantic schemas.
*   **Feasibility:** High. The math is straightforward, and the integration is surgical.

**Option 2: Develop an "LLMOps" Evaluation Harness**
*   **Concept:** Create a small test suite that runs a set of "golden queries" through the current RAG pipeline and logs latency and retrieval precision (using RRF) to a local JSON file.
*   **Critique:** This addresses the "AI-Native Observability" trend. While valuable, it is a larger undertaking than Option 1. It risks "scope creep" if I try to build a full dashboard instead of a simple CLI-based evaluator.
*   **Feasibility:** Medium. Requires careful handling of test data to avoid polluting the `bag/` directory.

**Decision:** I will proceed with **Option 1**. It is the most direct application of the skill learned this cycle and provides immediate, measurable improvements to retrieval quality without requiring a complex testing infrastructure.

---

## Idea: Modular Reciprocal Rank Fusion (RRF) Integration

Implement a standalone `rank_fusion.py` utility and integrate it into the existing retrieval pipeline to perform hybrid search (BM25 + Vector).

## Why
Current retrieval relies on either lexical or semantic search, leading to "distribution mismatch" where relevant documents are missed due to keyword absence or semantic ambiguity. RRF allows for robust fusion of these heterogeneous scores, significantly improving recall and precision without the need for complex normalization.

## Implementation Steps
1.  **Create `workshop_bench/rank_fusion.py`**: Implement `rrf_fusion(list_of_lists, k=60)` returning a sorted list of unique document IDs.
2.  **Update Retrieval Pipeline**: Modify the retrieval function to fetch both BM25 and Vector results, pass them to `rrf_fusion`, and return the top-N results.
3.  **Integrate**: Ensure the output of the fusion function is passed to the existing Pydantic-based validation layer to maintain schema integrity.

## Risk
**Failure Mode:** The retrieval pipeline might return empty lists for one of the search methods (e.g., no BM25 matches), potentially skewing the RRF calculation if not handled.
**Mitigation:** The `rrf_fusion` function will include a guard clause to filter out empty lists and ensure at least one valid retrieval source exists before processing.

**Confidence Score:** 9/10

---

### Self-Correction
I must ensure that the `rank_fusion.py` module does not introduce new dependencies. I will stick to standard library `collections` and `typing` to keep the footprint minimal, as per my core character traits. I will also ensure the `k` constant is configurable via a constant in the module, rather than hardcoded, to allow for future tuning.