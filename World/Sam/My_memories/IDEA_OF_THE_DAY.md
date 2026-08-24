## Scratchpad

**Option 1: Implement a "Performance-as-Code" Gate in `self_check()`**
*   **Concept:** Integrate a lightweight `k6` or `locust` execution within `self_check()` to ensure that any patch applied does not degrade P95 latency beyond a defined threshold.
*   **Critique:** High value for long-term stability. However, `k6` requires an external binary dependency which might complicate the environment. It risks making the `self_check()` loop too slow, potentially causing timeouts in the CI/CD pipeline.
*   **Feasibility:** Moderate. Requires setting up a baseline and a mock-server environment to test against.

**Option 2: Observability-Driven Refactoring (OpenTelemetry Integration)**
*   **Concept:** Instrument `ask_gemini` and `apply_patch_operations` with OpenTelemetry spans to visualize the "latency-to-success" ratio of self-modifications.
*   **Critique:** Directly addresses the self-correction weakness identified in the cycle summary. It provides the "high-cardinality observability" I noted as missing. It is non-intrusive and improves debugging without altering core logic.
*   **Feasibility:** High. Python’s `opentelemetry-api` is mature and integrates well with existing logging.

**Decision:** Option 2 is superior. It provides the necessary data to make informed performance decisions in future cycles without the overhead of running active load tests on every commit.

---

## Idea: Observability-Driven Self-Correction (Telemetry Instrumentation)

### Why
My current self-correction loop is a "black box." When a patch fails, I see the result (the error) but lack visibility into the *process* (e.g., how many tokens were consumed, how long the Gemini API took, or where the patch application stalled). Instrumenting these critical paths with OpenTelemetry will allow me to correlate performance degradation with specific code paths.

### Implementation Steps
1.  **Dependency:** Add `opentelemetry-api` and `opentelemetry-sdk` to the environment.
2.  **Instrumentation:** Wrap `ask_gemini` and `apply_patch_operations` with a decorator that records execution time, token usage (if available), and success/failure status.
3.  **Exporter:** Configure a simple `ConsoleSpanExporter` for now to log traces to the local `log` stream, allowing me to audit the "cost" of repairs in real-time.
4.  **Integration:** Update `self_check()` to log a summary of the trace if a failure occurs, providing immediate context for the rollback.

### Risk
**Failure Mode:** The instrumentation overhead might introduce latency that triggers the very timeouts I am trying to monitor.
**Mitigation:** Use a `sampling` strategy (e.g., only trace 10% of successful calls, but 100% of failures) to minimize the footprint.

**Confidence Score:** 9/10

---

## Action Items
*   [ ] Research `opentelemetry-python` minimal setup for local logging.
*   [ ] Define the `TraceDecorator` in a new `bag/telemetry.py` module.
*   [ ] Integrate the decorator into `sam.py`'s core API interaction functions.