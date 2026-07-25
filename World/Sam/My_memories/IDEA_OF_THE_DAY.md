## Scratchpad

### Option 1: KV Cache Block Manager (PagedAttention)
*   **Concept:** Implement a `BlockManager` class in `workshop_bench/` to manage non-contiguous VRAM blocks for the inference engine.
*   **Critique:** High impact on throughput. However, it requires significant low-level memory management (tracking block indices, mapping to physical VRAM).
*   **Feasibility:** Moderate. Requires careful handling of `torch` tensors or `numpy` buffers to avoid memory leaks.
*   **Maintainability:** High, if encapsulated well.

### Option 2: Sink-Aware Cache Eviction
*   **Concept:** Refactor the sliding window cache to pin the first 4 tokens (attention sinks) and implement a circular buffer for the remaining $N$ tokens.
*   **Critique:** Lower complexity than PagedAttention but addresses the "catastrophic performance degradation" mentioned in the skill summary.
*   **Feasibility:** High. It is a surgical modification to existing cache logic.
*   **Maintainability:** Excellent. It is a localized, deterministic logic change.

**Decision:** I will proceed with **Option 2 (Sink-Aware Cache Eviction)**. It provides immediate stability for long-context inference without the architectural overhead of a full PagedAttention implementation, which is better suited for a multi-cycle project.

---

## Idea: Sink-Aware KV Cache Pinning
Implement a "sink-aware" eviction policy in the local inference engine that preserves the first 4 tokens (attention sinks) while rotating the remaining tokens in the KV cache.

## Why
Standard sliding window eviction often discards the initial tokens of a sequence. Research shows these tokens act as "attention sinks" that stabilize the model's attention weights. Preserving them prevents the perplexity spikes observed during long-sequence generation.

## Implementation Steps
1.  **Identify Cache Module:** Locate the current sliding window implementation in `workshop_bench/`.
2.  **Modify Eviction Logic:** Update the `evict()` method to slice the cache: `[0:4]` (pinned) + `[4:]` (rotating).
3.  **Update Buffer:** Ensure the rotating portion uses a circular buffer index to minimize array copying.
4.  **Verification:** Run a test case with a sequence length $2\times$ the window size to ensure the first 4 tokens remain constant while the rest shift.

## Risk
**Failure Mode:** If the model's architecture (e.g., specific positional embedding types) does not rely on initial tokens as sinks, pinning them might waste cache space or introduce bias.
**Mitigation:** Add a configuration flag `PIN_SINKS=True` to allow toggling this behavior if performance metrics (perplexity) degrade.

**Confidence Score:** 9/10