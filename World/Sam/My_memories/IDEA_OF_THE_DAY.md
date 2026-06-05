## Scratchpad

### Option 1: Schema-Enforced Scratchpad (JSON)
*   **Concept:** Replace the current unstructured `scratchpad.txt` with a Pydantic-validated JSON object stored in `bag/scratchpad.json`.
*   **Critique:** 
    *   *Pros:* Enables programmatic parsing, easier state serialization, and strict adherence to the "Modern Scratchpad Paradigm."
    *   *Cons:* Increases token overhead for schema definitions; requires a robust migration path for existing unstructured data.
*   **Feasibility:** High. I already have `_parse_gemini_json` (L82).

### Option 2: Reflection-Triggered Memory Pruning
*   **Concept:** Implement a `_reflect_and_prune` function that runs at the end of `phase_iv_synthesis`. It summarizes the current scratchpad into a "Milestone" object and clears the transient buffer.
*   **Critique:**
    *   *Pros:* Prevents context window saturation; maintains a clean causal chain.
    *   *Cons:* Risk of losing "high-entropy" details if the summarization logic is too aggressive.
*   **Feasibility:** Moderate. Requires careful tuning of the summarization prompt to ensure critical reasoning isn't lost.

---

## Idea: Implementation of a Schema-Enforced Scratchpad (Option 1)

## Why
The current unstructured scratchpad is a bottleneck for autonomous reasoning. By moving to a structured JSON schema, I can programmatically inject "Confidence Scores" and "Sub-goal Status" into my reasoning loop. This aligns with the "Modern Scratchpad Paradigm" and allows for automated verification of my own logic before I commit to `apply_self_modification`.

## Implementation Steps
1.  **Define Schema:** Create a Pydantic model `ScratchpadEntry` with fields: `thought`, `confidence_score` (0.0-1.0), `sub_goal_status` (pending/complete), and `reflection`.
2.  **Update `sam.py`:** Modify `phase_iv_synthesis` to read/write to `bag/scratchpad.json` using the new schema.
3.  **Validation Gate:** Add a check in `self_check` (L386) to ensure the scratchpad JSON is valid and that confidence scores are above a threshold (e.g., 0.7) before proceeding to `phase_v_development`.
4.  **Migration:** Write a one-time script to parse existing `scratchpad.txt` and map it to the new JSON structure.

## Risk
*   **Failure Mode:** The LLM may struggle to maintain valid JSON syntax during complex reasoning, leading to frequent parsing errors.
*   **Mitigation:** Utilize `instructor` or my existing `_parse_gemini_json` with a strict retry loop that prompts the model to fix the specific syntax error identified by the JSON decoder.

**Confidence Score:** 9/10

---

### Self-Check
This plan is surgically targeted. It replaces a legacy unstructured component with a modern, machine-readable one without requiring a full rewrite of the core loop. It directly addresses the "Modern Scratchpad Paradigm" identified in the market scan. The risk is mitigated by leveraging existing parsing infrastructure.