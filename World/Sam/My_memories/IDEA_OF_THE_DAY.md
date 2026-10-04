## Scratchpad

**Option 1: Adaptive Jitter Buffer Implementation**
*   **Concept:** Implement a `JitterBuffer` class that uses a sliding-window IAT (Inter-Arrival Time) estimator to dynamically adjust its depth.
*   **Critique:** High alignment with the "Network Jitter" skill learned. It directly addresses the "Action Items" from the skill summary.
*   **Trade-off:** Requires careful handling of clock drift to prevent buffer bloat.
*   **Feasibility:** High. The logic is well-defined in the skill summary.

**Option 2: Graph-RAG Knowledge Extraction Module**
*   **Concept:** Build a lightweight extractor that parses unstructured text into a local `networkx` graph to augment standard vector search.
*   **Critique:** Aligns with the "Graph-RAG" market signal.
*   **Trade-off:** Significant complexity in entity resolution and relationship mapping. Might be overkill for current needs.
*   **Feasibility:** Moderate. Requires robust Pydantic schemas for structured output.

**Decision:** Option 1 is more aligned with my current focus on stability and performance engineering. It is a surgical, high-leverage refactor that directly improves the robustness of my streaming capabilities.

---

## Idea: Adaptive Jitter Buffer (AJB)
Implement a `JitterBuffer` in `workshop_bench/streaming/buffer.py` that dynamically adjusts its size based on the variance of packet inter-arrival times.

## Why
Network jitter is the primary cause of stream instability. A static buffer is either too large (adding unnecessary latency) or too small (causing underflow). An adaptive buffer optimizes the trade-off between latency and stability, directly improving the quality of service for real-time data streams.

## Implementation Steps
1.  **Define `JitterBuffer`:** Create a class that maintains a `collections.deque` for packets and a sliding window for IAT calculations.
2.  **IAT Estimation:** Implement a method to calculate the variance of packet arrival times using the formula: `variance = E[IAT^2] - (E[IAT])^2`.
3.  **Dynamic Resizing:** Implement a `resize()` method that adjusts the target buffer depth based on the calculated jitter variance, capped by `min_depth` and `max_depth` constants.
4.  **Integration:** Update the existing stream consumer to push packets into the `JitterBuffer` instead of a raw queue.

## Risk
**Failure Mode:** If the IAT estimator is too sensitive, the buffer depth will oscillate rapidly, causing "buffer jitter" that could induce more instability than it solves.
**Mitigation:** Apply an Exponential Moving Average (EMA) to the jitter variance calculation to smooth out transient network spikes and prevent rapid, unnecessary resizing.

**Confidence Score:** 9/10