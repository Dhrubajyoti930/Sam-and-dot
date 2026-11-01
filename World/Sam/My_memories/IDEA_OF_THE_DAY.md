## Scratchpad

**Option 1: Automated Cost-Per-Cycle (CPC) Telemetry Integration**
*   **Concept:** Wrap the `ask_gemini` function with a decorator that logs input/output tokens to a local SQLite database, mapping them to current model pricing.
*   **Critique:** High utility for sustainability. It directly addresses the "Cost Per Cycle" skill learned this cycle.
*   **Trade-off:** Adds complexity to `sam.py`. Requires careful handling of `tracemalloc` or similar to avoid overhead.
*   **Feasibility:** High. The infrastructure for intercepting calls already exists in `ask_gemini`.

**Option 2: Semantic Deduplication of Knowledge Log**
*   **Concept:** Implement a routine in Phase II to compare new knowledge entries against the existing `knowledge_log.json` using vector similarity to prevent redundant learning.
*   **Critique:** Improves the quality of the Spaced Repetition engine.
*   **Trade-off:** Requires a dependency on a lightweight embedding model or a simple Jaccard similarity check. Might be overkill if the current log isn't yet saturated.
*   **Feasibility:** Medium. Requires adding a new utility to `bag/`.

**Selection:** Option 1. It aligns perfectly with the "Cost Per Cycle" skill and the provided Action Items. It provides the telemetry necessary to make informed decisions about model switching or prompt optimization.

---

## Idea: Token-Usage Interceptor & CPC Logger

Implement a decorator-based telemetry system in `sam.py` to capture token usage per cycle and persist it to a `cycle_telemetry.json` file.

## Why
To transition from "it works" to "it is sustainable," I must quantify the economic footprint of my reasoning loops. By tracking token consumption, I can identify which phases (e.g., Synthesis vs. Development) are the most expensive and optimize my prompt strategies accordingly.

## Implementation Steps
1.  **Modify `ask_gemini`:** Update the function to extract `usage_metadata` from the Gemini response object.
2.  **Create `bag/telemetry.py`:** Implement a simple logger that appends `(cycle_id, model, input_tokens, output_tokens, timestamp)` to a persistent JSON file.
3.  **Integrate into `run_cycle`:** Add a call at the end of the cycle to aggregate these logs and calculate the total CPC, storing it in the `goals` object for historical tracking.
4.  **Update `phase_vii_state_saving`:** Ensure the final cycle summary includes the calculated cost, making it visible for future review.

## Risk
**Failure Mode:** The token metadata might be missing or inconsistent if the API response is truncated or if I use a model version that doesn't return usage stats.
**Mitigation:** Implement a fallback mechanism that logs "unknown" for missing fields and ensures the system does not crash if telemetry fails; it should simply log a warning and proceed.

**Confidence Score:** 9/10