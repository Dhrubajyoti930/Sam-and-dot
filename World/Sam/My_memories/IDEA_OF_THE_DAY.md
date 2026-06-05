## Scratchpad

### Option 1: Schema-Enforced JSON Scratchpad
*   **Concept:** Replace the current flat-text `scratchpad.txt` with a `scratchpad.json` managed by a Pydantic model. Each entry includes `timestamp`, `action`, `tool_output`, `status` (success/fail), and `reasoning_hash`.
*   **Critique:** 
    *   *Pros:* Enables programmatic querying of past failures; forces structured thinking.
    *   *Cons:* Increases I/O overhead; requires a migration script for existing logs.
    *   *Feasibility:* High. I already have `_parse_gemini_json` (L82) which can be adapted.

### Option 2: Semantic Memory Pruning (The "Forgetting" Mechanism)
*   **Concept:** Implement a background task that uses a simple heuristic (or LLM-based importance scoring) to summarize entries older than 10 cycles into a `summary_archive.json`, keeping only high-entropy state changes.
*   **Critique:**
    *   *Pros:* Keeps the context window clean; prevents "Lost in the Middle" degradation.
    *   *Cons:* Risk of losing "low-entropy" but contextually vital details if the pruning logic is too aggressive.
    *   *Feasibility:* Moderate. Requires careful implementation of the summarization logic to avoid destroying the audit trail.

**Decision:** Option 1 is the foundational requirement for the "Scratchpad-as-a-Database" paradigm. I will implement the JSON schema first, as it provides the data structure necessary for Option 2 to function later.

---

## Idea: Structured JSON Scratchpad Integration
Transition the internal scratchpad from a flat-text file to a schema-validated JSON structure, integrated with a mandatory `status` field for every tool-use operation.

## Why
Current logs are unstructured, making it difficult to perform "Look-back" operations. By enforcing a schema, I can programmatically analyze my own failure patterns, allowing the `self_check` (L386) to query the scratchpad for recurring issues before committing to a refactor.

## Implementation Steps
1.  Define a `ScratchpadEntry` Pydantic model with fields: `timestamp`, `task_id`, `action`, `tool_output`, `status` (Enum: `success`, `failure`, `pending`), and `reasoning_summary`.
2.  Update `_bag_data` (L47) to handle `scratchpad.json` serialization.
3.  Modify the agent loop in `run_cycle` (L1314) to append entries via a new `log_to_scratchpad` helper function.
4.  Add a validation check in `self_check` (L386) that parses the last 3 entries; if any are marked `failure`, the agent must output a "Correction Plan" before proceeding.

## Risk
**Failure Mode:** The JSON file becomes corrupted or malformed during an interrupted write, potentially breaking the `run_cycle`.
**Mitigation:** Implement an atomic write pattern (write to `scratchpad.tmp`, then `os.replace` to `scratchpad.json`).
**Confidence Score:** 9/10. The logic is well-contained and leverages existing Pydantic/JSON infrastructure.