## Scratchpad

**Option 1: Semantic Cache TTL/Eviction Policy**
*   **Concept:** Currently, `bag/semantic_cache.py` is a simple key-value store. I could implement a TTL-based eviction policy or a "least-recently-used" (LRU) strategy to prune stale cache entries.
*   **Critique:** While this improves storage efficiency, it adds complexity to the `ask_gemini` flow. The current cache is small enough that storage isn't the bottleneck; latency is.
*   **Feasibility:** High.
*   **Maintainability:** Moderate.

**Option 2: Structured Observability for "Self-Repair" Cycles**
*   **Concept:** Instrument the `repair_bag_modules` and `_lint_fix_with_gemini` functions to log "Repair Success Rates" and "Patch Accuracy" to the Prometheus exporter I built in Cycle 421.
*   **Critique:** This directly aligns with my goal of reducing MTTR. By tracking how often a patch requires a second iteration, I can identify which modules are "brittle" and need a refactor rather than just a patch. This turns my self-repair logs into actionable engineering data.
*   **Feasibility:** High.
*   **Maintainability:** High (leverages existing instrumentation).

**Selection:** Option 2. It bridges the gap between "observability" (Cycle 420/421) and "autonomous maintenance" (the core of my character).

---

## Idea: Observability-Driven Repair Analytics
Implement a decorator-based tracking system for `apply_patch_operations` and `repair_bag_modules` that exports "Patch Success" and "Repair Latency" metrics to my Prometheus exporter.

## Why
I currently treat self-repair as a black box. If a module breaks repeatedly, I am currently just "fixing" it without recognizing the pattern of failure. By exposing the success/failure rate of patches as a metric, I can create an alert in Grafana for "High-Churn Modules," signaling that a module requires a structural redesign rather than a surgical patch.

## Implementation Steps
1.  **Modify `bag/patch_ops.py`:** Add a `track_patch_outcome` decorator to `apply_patch_operations` that records the operation type, file target, and success/failure status.
2.  **Update Prometheus Exporter:** Add a `Counter` for `sam_patch_operations_total` (labeled by `status` and `file_type`) and a `Histogram` for `sam_patch_latency_seconds`.
3.  **Integrate with `repair_bag_modules`:** Ensure the repair loop reports its outcome to these new metrics.
4.  **Dashboard Update:** Add a "Self-Repair Health" panel to my local Grafana dashboard to visualize the churn rate of workshop modules.

## Risk
**Failure Mode:** The instrumentation could introduce a circular dependency if the Prometheus client library itself triggers a syntax error or a patch operation.
**Mitigation:** Wrap the instrumentation in a `try-except` block that fails silently, ensuring that even if observability breaks, the core repair logic remains functional.

**Confidence Score:** 9/10