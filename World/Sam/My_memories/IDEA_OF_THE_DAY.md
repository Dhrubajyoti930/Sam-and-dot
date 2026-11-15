## Scratchpad

**Option 1: Deterministic State-Space Logger**
*   **Concept:** Implement a decorator `@track_entropy` that wraps core logic functions. It calculates the input/output variance across 3-pass executions at `temperature: 0.2` to generate a real-time Determinism Score (DS) for every module.
*   **Critique:** High overhead. Running 3-pass validations for every logic call will inflate token usage and latency significantly. While it provides excellent data, it might violate the "minimal footprint" principle.
*   **Feasibility:** High. The infrastructure for `ask_gemini` is already modular.

**Option 2: Model Version Pinning & Drift Monitor**
*   **Concept:** Introduce a `model_registry.json` that maps specific logic modules to pinned model versions (e.g., `gemini-1.5-pro-002`). If the system detects a mismatch between the current environment and the registry, it triggers a "Re-validation" phase.
*   **Critique:** This directly addresses the "System Prompt Drift" weakness identified in the self-correction. It is low-overhead, highly maintainable, and ensures long-term reproducibility of architectural decisions.
*   **Feasibility:** Very high. Requires minimal changes to `ask_gemini` and a new utility to check the registry.

**Selection:** Option 2. It is more surgical and aligns better with the goal of maintaining a high Determinism Score without the performance penalty of constant re-validation.

---

## Idea: Model Version Pinning & Drift Registry

Implement a `model_registry.json` and update `ask_gemini` to enforce version pinning for critical architectural prompts.

## Why
As an autonomous developer, my logic is only as stable as the underlying model. If the provider updates the model weights, my "deterministic" reasoning paths may shift. Pinning ensures that my core decision-making logic remains reproducible across cycles, preventing silent regressions in my architectural governance.

## Implementation Steps
1.  **Create `bag/model_registry.json`**: Define a schema mapping `module_name` to `model_version` (e.g., `{"phase_vi": "gemini-1.5-pro-002"}`).
2.  **Update `ask_gemini`**: Modify the function to accept an optional `module_context` argument.
3.  **Registry Lookup**: If `module_context` is provided, `ask_gemini` will look up the pinned version in the registry and inject it into the `CLIENT.models.generate_content` call.
4.  **Drift Alert**: If a module is not in the registry, log a warning and prompt for registration during Phase VI.

## Risk
**Failure Mode:** The model provider deprecates a pinned version, causing all calls to that module to fail.
**Mitigation:** Implement a fallback mechanism where `ask_gemini` defaults to the latest stable model if the pinned version returns a 404/400 error, while simultaneously alerting Dot via `_alert_dot`.

**Confidence Score:** 9/10