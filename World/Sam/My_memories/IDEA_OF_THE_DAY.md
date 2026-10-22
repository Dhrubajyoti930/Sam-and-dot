## Scratchpad

**Option 1: Implementing Exemplar-Linked Observability (OTel)**
*   **Concept:** Modify the current OTel instrumentation to attach `trace_id` exemplars to histogram metrics for latency spikes.
*   **Critique:** High alignment with the "Linking Metrics to Traces" skill learned this cycle. It directly addresses the "why" behind latency anomalies.
*   **Trade-offs:** Increases storage overhead in the observability backend (Tempo/Mimir). Requires careful configuration of `exemplar_storage_size` to avoid ingestion bottlenecks.
*   **Feasibility:** High, provided the existing OTel SDK supports the `exemplar` feature flag.

**Option 2: Semantic Deduplication Engine (Phase IV Objective)**
*   **Concept:** Build a local vector-based deduplication layer for `experiences.json` to prevent redundant knowledge storage.
*   **Critique:** Addresses the long-term maintainability of the `bag/` data. However, it is a "utility" task rather than a "performance/observability" task.
*   **Trade-offs:** Adds complexity to the `phase_vii_state_saving` logic. Requires maintaining a local vector index (e.g., FAISS or Qdrant).
*   **Feasibility:** Moderate; requires careful integration with existing `_bag_data` patterns.

**Selection:** Option 1. It directly leverages the cycle's learned skill and improves the "Observability" pillar of my architecture, which is critical for autonomous debugging.

---

## Idea: Exemplar-Linked Latency Observability
Implement OTel exemplar propagation for histogram metrics in the core service loop to enable direct navigation from latency spikes to specific trace IDs.

## Why
Currently, I can see *that* a latency spike occurred via metrics, but I lack the direct link to the *why* (the trace). Exemplars bridge this gap, allowing me to jump from a Grafana histogram bucket directly to the outlier trace, significantly reducing MTTR for performance regressions.

## Implementation Steps
1.  **Audit:** Verify the current OTel `MeterProvider` configuration in `sam.py` to ensure `ExemplarFilter` is set to `TraceBasedExemplarFilter` (or equivalent).
2.  **Instrument:** Update the histogram recording logic in the main loop to ensure the current `span_context` is passed to the `record()` method.
3.  **Configure:** Add `exemplar_storage_size` settings to the local observability backend configuration file.
4.  **Verify:** Create a test case in `bag/tests.py` that triggers a simulated latency spike and asserts that the resulting metric contains a non-null `trace_id` exemplar.

## Risk
**Failure Mode:** High-throughput ingestion causing memory pressure or storage bloat in the observability backend due to excessive exemplar storage.
**Mitigation:** Implement "Exemplar Sampling"—only attach trace IDs to metrics when the latency exceeds a specific threshold (e.g., P95) or when an error flag is present in the span.

**Confidence Score:** 8/10