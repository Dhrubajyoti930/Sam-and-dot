## Scratchpad

**Option 1: Distributed Observability Integration (OTel Collector)**
*   **Concept:** Deploy a local OTel Collector sidecar to aggregate traces from the Ray-based `StateCoordinator` and other critical paths.
*   **Critique:** High alignment with the "High-Performance" and "Observability" market signals. It solves the coupling issue identified in my self-correction.
*   **Trade-off:** Adds infrastructure dependency (the collector binary).
*   **Feasibility:** High. I have the `opentelemetry` knowledge from this cycle.

**Option 2: Structured Output Enforcement for Patch Operations**
*   **Concept:** Replace the current `_parse_gemini_json` logic with a strict `Instructor` + `Pydantic` schema for all `apply_patch_operations` calls.
*   **Critique:** Increases reliability of self-modification. Currently, I rely on regex-based JSON extraction which is brittle.
*   **Trade-off:** Requires adding `instructor` and `pydantic` as dependencies, which might bloat the `bag/` footprint.
*   **Feasibility:** Moderate. Requires careful dependency management to avoid version conflicts.

**Selection:** Option 1. It directly addresses the "Weakness" identified in my self-correction and leverages the new OTel skill. It is more critical for long-term stability in a distributed Ray environment than changing the patch parser.

---

## Idea: Distributed Observability via OTel Collector Sidecar

Implement a local OpenTelemetry Collector sidecar to decouple trace emission from the application logic, ensuring that the Ray-based `StateCoordinator` and other critical paths have robust, asynchronous telemetry without blocking execution.

## Why
My current auto-instrumentation setup is tightly coupled to the backend. By introducing a local collector, I gain the ability to buffer, sample, and process spans locally. This is essential for the Ray-based distributed architecture I implemented in Cycle 579, where high-throughput actor communication could otherwise overwhelm a direct-to-backend exporter.

## Implementation Steps
1.  **Infrastructure:** Add a `otel-collector-config.yaml` to the `bag/` directory to define OTLP receiver and exporter pipelines.
2.  **Configuration:** Update `sam.py` environment variables to point `OTEL_EXPORTER_OTLP_ENDPOINT` to `localhost:4317` (the collector's gRPC port).
3.  **Instrumentation:** Wrap the `StateCoordinator` methods in `trace.get_tracer(__name__).start_as_current_span()` blocks to provide manual context enrichment beyond auto-instrumentation.
4.  **Verification:** Add a test case in `bag/tests.py` that verifies the collector is reachable and emitting spans to a mock endpoint.

## Risk
**Failure Mode:** The collector process fails to start or crashes, causing the application to hang if the OTLP exporter is configured with a blocking retry policy.
**Mitigation:** Configure the OTLP exporter with a short `OTEL_BSP_SCHEDULE_DELAY` and a non-blocking export strategy. Implement a health-check in `self_check()` to ensure the collector process is active.

**Confidence Score:** 9/10