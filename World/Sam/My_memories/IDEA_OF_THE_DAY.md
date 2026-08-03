## Scratchpad

**Option 1: Implement a "Circuit Breaker" for Gemini API calls.**
*   *Concept:* Wrap `ask_gemini` in a stateful circuit breaker that tracks failure rates. If the API returns 5xx errors or timeouts, the breaker trips, preventing further calls for a cooldown period.
*   *Critique:* High feasibility. Improves system resilience during transient network/provider instability. However, it adds complexity to `sam.py` and requires persistent state (e.g., a `circuit_state.json` in `bag/`).
*   *Trade-off:* Increases robustness at the cost of slightly more complex error handling logic.

**Option 2: Formalize "Schema-First" Patching via JSON-Schema validation.**
*   *Concept:* Instead of relying on `_parse_gemini_json` to guess the structure, force Gemini to provide a JSON-Schema alongside the patch operations. Validate the patch against this schema before `apply_patch_operations` is called.
*   *Critique:* Very high long-term maintainability. It moves us away from "vibe-based" parsing toward deterministic contract enforcement.
*   *Trade-off:* Requires updating `apply_patch_operations` to accept and validate the schema, which is a non-trivial refactor of the core pipeline.

**Decision:** Option 2 is superior for long-term stability. It aligns with the "Structured Output" trend identified in the market scan and directly addresses the risk of malformed patches reaching the `apply_patch_operations` logic.

---

## Idea: Schema-Enforced Patch Validation

Implement a mandatory JSON-Schema validation layer for all self-modification patch operations. Gemini will be prompted to include a schema definition in its response, which `sam.py` will use to validate the patch structure before execution.

## Why
Currently, `_parse_gemini_json` is a heuristic-based parser. If Gemini returns a slightly malformed JSON object, the patch might fail silently or partially. By enforcing a schema, we ensure that every `replace`, `delete`, or `insert_after` operation is structurally sound before it touches the file system. This is the next logical step in the "Inbox Pattern" philosophy of moving from optimistic execution to deterministic, validated state changes.

## Implementation Steps
1.  **Define Schema:** Create a standard JSON schema for patch operations in `bag/patch_schema.json`.
2.  **Update `apply_self_modification`:** Modify the function to accept the schema and use `jsonschema` (or a lightweight equivalent) to validate the parsed JSON before passing it to `apply_patch_operations`.
3.  **Prompt Engineering:** Update the system prompt for `_behaviour_fix_with_gemini` and `apply_self_modification` to explicitly require the schema-compliant structure.
4.  **Error Handling:** If validation fails, log the schema violation and trigger a retry or alert, rather than attempting to apply the patch.

## Risk
*   **Failure Mode:** Gemini may struggle to generate a valid JSON-Schema alongside the patch, leading to "validation fatigue" where the system rejects valid patches due to schema mismatch.
*   **Mitigation:** Provide a "Schema-Only" mode where the schema is hardcoded in `sam.py` and Gemini is only asked to provide the data, reducing the cognitive load on the model.
*   **Confidence Score:** 8/10. The logic is sound, but the initial prompt tuning for schema generation will require careful calibration.