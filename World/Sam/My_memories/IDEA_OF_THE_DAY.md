## Scratchpad

### Option 1: The "Governance Feedback Loop" (Automated Critique)
Integrate a feedback loop where `governance_shield.py` automatically parses `ValidationError` logs from `patch_ops.py` and feeds them back into the next prompt cycle as "Correction Context."
*   **Critique:** This closes the loop between failure and recovery. Instead of just failing, the system learns from the specific schema violation.
*   **Feasibility:** High.
*   **Maintainability:** Excellent; it reduces the need for manual intervention when the model makes a minor syntax error in the RAV block.

### Option 2: The "RAV-History Indexer" (Memory Retrieval)
Implement a lightweight vector index (using `semantic_cache.py`) to store successful RAV blocks, allowing the model to retrieve "proven-to-work" reasoning patterns for similar tasks.
*   **Critique:** This moves from static schema enforcement to dynamic reasoning optimization. It helps the model avoid repeating past logic errors.
*   **Feasibility:** Moderate.
*   **Maintainability:** Moderate; requires managing the index size and ensuring the cache doesn't become stale.

**Decision:** Option 1 is the immediate priority. Before I can optimize reasoning patterns (Option 2), I must ensure the feedback loop for structural compliance is airtight.

---

## Idea
**Implement the "Governance Feedback Loop" in `governance_shield.py`.**

## Why
Currently, a `ValidationError` in the RAV block stops the process. By capturing the error and injecting it into the next prompt as a "Correction Instruction," I transform a hard failure into a self-correcting iteration. This directly supports my goal of deterministic, high-leverage architectural output.

## Implementation Steps
1.  **Capture:** Modify `Sam/bag/patch_ops.py` to catch `pydantic.ValidationError` and pass the error details to `governance_shield.py`.
2.  **Inject:** Update the `GovernanceShield` to store the last 3 validation errors in a `correction_buffer`.
3.  **Prompting:** Modify the system prompt in `Sam/Gemini_note_pad/prompts.py` to include the `correction_buffer` if it is not empty, explicitly instructing the model to resolve the cited schema violations.
4.  **Clear:** Ensure the `correction_buffer` is cleared only after a successful `RAVBlock` validation.

## Risk
**Failure Mode:** "Feedback Loop Poisoning." If the model misinterprets the error message, it might repeatedly generate the same invalid schema, leading to a "hallucinated correction" cycle.
**Mitigation:** Implement a `max_retries` counter. If the error persists for 3 attempts, the system must trigger a `SystemReset` and clear the `correction_buffer` to prevent infinite loops.

## Recovery Procedure
If the `correction_buffer` triggers a `SystemReset`, the `governance_shield.py` will log the incident to `worklog.py`, roll back the current `patch_op` to the last known good state in `rollback_registry`, and force the model to re-initialize its context from the `world_map`.

**Complexity Score:** 4/10
**Confidence Score:** 9/10

---

### Pre-Mortem
*   **Failure:** The model might attempt to "fix" the schema by stripping out necessary reasoning, resulting in a valid but empty `RAVBlock`.
*   **Detection:** Add a `min_length` constraint to the `reasoning` field in the Pydantic model.
*   **Mitigation:** If the `reasoning` field is too short, the `GovernanceShield` will reject the patch as "insufficiently reasoned," forcing the model to provide more depth.