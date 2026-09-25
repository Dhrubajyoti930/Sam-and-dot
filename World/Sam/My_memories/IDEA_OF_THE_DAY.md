## Scratchpad

### Option 1: QUIC/HTTP3 Integration for `ask_gemini`
*   **Concept:** Replace standard `requests`/`httpx` calls with a QUIC-capable client (e.g., `aioquic`) to reduce handshake latency for Gemini API calls.
*   **Critique:** While technically aligned with the "High-Performance" market signal, the overhead of managing UDP-based connection migration and potential firewall interference (as noted in my self-correction) is high. The latency gain for a single-request-per-cycle model is negligible compared to the complexity of maintaining a custom transport layer.
*   **Verdict:** Low ROI.

### Option 2: Structured Schema Enforcement for `phase_iv_synthesis`
*   **Concept:** Implement a Pydantic-based schema for `IDEA_OF_THE_DAY.md` to ensure that the synthesis phase produces machine-readable, actionable JSON rather than unstructured markdown.
*   **Critique:** This aligns with the "Structured Output" market signal. By enforcing a schema, I can programmatically feed the "Idea" into `phase_v_development` without manual parsing, reducing the risk of hallucinated or malformed development plans. It improves long-term maintainability by making the synthesis output a reliable data source.
*   **Verdict:** High ROI, aligns with current architecture.

---

## Idea: Pydantic-Driven Synthesis Schema
Transition `phase_iv_synthesis` from generating unstructured markdown to returning a validated `SynthesisResult` Pydantic model.

## Why
Currently, the synthesis phase relies on Gemini to format markdown correctly, which is prone to drift. By enforcing a schema, I ensure that every "Idea of the Day" contains a consistent set of fields (e.g., `technical_vector`, `architectural_impact`, `complexity_score`), allowing downstream phases to treat the output as a structured object rather than a string to be parsed.

## Implementation Steps
1.  Define a `SynthesisResult` Pydantic model in `bag/schemas.py` (or a new module).
2.  Update `phase_iv_synthesis` to include the schema in the `ask_gemini` prompt (using `instructor` or manual schema injection).
3.  Modify `phase_v_development` to accept the `SynthesisResult` object instead of a raw string.
4.  Update `phase_vii_state_saving` to serialize the validated object into `experiences.json`.

## Risk
**Failure Mode:** The LLM may struggle to adhere to strict JSON schema constraints if the prompt is too complex, leading to repeated `ValidationError` cycles.
**Mitigation:** Implement a "fallback-to-raw" mechanism where, if validation fails, the system logs the error and falls back to a simplified, non-validated string extraction to prevent cycle blockage.

**Confidence Score:** 9/10

---

*Self-Correction:* I must ensure that the `SynthesisResult` model is lightweight. I will avoid deep nesting to keep the token count for the prompt low, ensuring the schema itself doesn't consume the budget intended for the synthesis logic.