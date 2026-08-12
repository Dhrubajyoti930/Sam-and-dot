## Scratchpad

**Option 1: Distributed Transaction Coordinator (Saga Pattern)**
*   **Concept:** Implement a `SagaManager` in `bag/` to handle multi-step operations across the `workshop_bench/` modules, ensuring that if one step fails, compensating actions are triggered to revert state.
*   **Critique:** High complexity. It requires tracking state across multiple files. While it aligns with the "Shared-Nothing Architecture" learning, it might be overkill for Sam's current scale.
*   **Feasibility:** Moderate. Requires significant changes to `apply_patch_operations`.

**Option 2: Localized Inference Pipeline (Ollama Integration)**
*   **Concept:** Refactor `ask_gemini` to support a fallback or primary path using a local Ollama instance for non-critical tasks (e.g., lint-fixing, simple parsing).
*   **Critique:** Directly addresses the "Localized LLM Orchestration" market signal. Reduces dependency on external API latency and improves privacy.
*   **Feasibility:** High. The `ask_gemini` function is already modular.
*   **Trade-off:** Local models may struggle with the complex reasoning required for `phase_iv_synthesis` compared to Gemini 1.5 Pro.

**Selection:** Option 2. It aligns with the current market shift toward local orchestration and provides a tangible improvement to Sam's autonomy by reducing external API dependency.

---

## Idea: Local-First Inference Fallback
Implement a `LocalInferenceClient` within `bag/` that interfaces with Ollama. Modify `ask_gemini` to route low-complexity tasks (e.g., syntax-check, simple JSON parsing) to the local model, reserving Gemini for high-level synthesis and complex architectural planning.

## Why
1.  **Latency/Cost:** Reduces round-trip time for repetitive tasks.
2.  **Resilience:** Provides a "degraded mode" of operation if external API connectivity is interrupted.
3.  **Market Alignment:** Directly implements the "Localized LLM Orchestration" vector.

## Implementation Steps
1.  Create `bag/local_inference.py` to handle `ollama` library calls.
2.  Update `ask_gemini` in `sam.py` to accept a `priority` parameter.
3.  If `priority == "low"`, attempt local inference first; fallback to Gemini on failure.
4.  Update `repair_bag_modules` to use the local client for syntax-error detection and initial repair attempts.

## Risk
**Failure Mode:** The local model (e.g., Llama 3.1 8B) may hallucinate or fail to follow the strict JSON schema required for `apply_patch_operations`.
**Mitigation:** Implement a strict validation gate: if the local model's output fails `_parse_gemini_json` or `compile()`, the system must automatically discard the result and retry with the primary Gemini client.

**Confidence Score:** 8/10