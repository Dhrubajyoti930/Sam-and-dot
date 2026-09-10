## Scratchpad

**Option 1: Implement `resilience_baseline.md` and Fault Injection**
*   **Concept:** Create a formal baseline for "steady state" and a script to simulate latency in API dependencies.
*   **Critique:** This directly addresses the "Chaos Engineering" skill learned this cycle. It is highly actionable and aligns with my current focus on reliability.
*   **Trade-off:** Requires careful handling of `sam.py` to ensure the fault injection doesn't trigger a permanent state failure if the circuit breaker logic is flawed.
*   **Feasibility:** High. I have the `patch_ops` infrastructure to insert these hooks safely.

**Option 2: Integrate "LLM-as-a-Judge" for `SystemPulse` alerts**
*   **Concept:** Use a small local model to evaluate the severity of `SystemPulse` logs before alerting Dot.
*   **Critique:** This is a sophisticated evolution of my observability stack. However, it adds significant complexity to the `self_check` and `behaviour_check` loops.
*   **Trade-off:** High maintenance cost. If the judge model hallucinates, I might suppress critical alerts or spam Dot with noise.
*   **Feasibility:** Moderate. Requires setting up a local inference pipeline which might exceed my current resource footprint.

**Decision:** Option 1 is the superior choice for this cycle. It builds foundational resilience without over-engineering the observability layer.

---

## Idea: Resilience Baseline & Latency Injection Hook

Implement a `resilience_baseline.md` document defining the "Steady State" for my core API calls and a `fault_injector.py` module in `workshop_bench/` that allows for controlled latency injection into `ask_gemini` calls.

## Why
My recent cycles have focused on architecture and observability. To move from "reactive firefighting" to "proactive hardening," I must quantify what "normal" looks like and verify that my system handles degradation gracefully. This satisfies the "Chaos Engineering" skill acquisition.

## Implementation Steps
1.  **Create `resilience_baseline.md`:** Define latency thresholds (e.g., `ask_gemini` < 2s, `self_check` < 5s) and error rate limits.
2.  **Develop `workshop_bench/fault_injector.py`:** Create a context manager that can be wrapped around `ask_gemini` to simulate network latency or timeouts.
3.  **Patch `sam.py`:** Integrate a "Chaos Mode" toggle in `ask_gemini` that checks for a `chaos_config.json` file to trigger the injector during testing cycles.
4.  **Verification:** Run a test cycle where I inject a 500ms delay to ensure the `_stitch_gemini` logic handles the increased latency without timing out.

## Risk
**Failure Mode:** The fault injector might accidentally trigger during a production-critical task if the `chaos_config.json` is not properly scoped to test environments.
**Mitigation:** The `fault_injector` will explicitly check for a `SAM_ENV == "testing"` environment variable before applying any latency. If the variable is missing, it defaults to a no-op.

**Confidence Score: 9/10**