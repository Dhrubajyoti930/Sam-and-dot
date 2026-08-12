## Scratchpad

**Option 1: Reactive Dataflow Pipeline for `phase_v_development`**
*   **Concept:** Refactor the development planning phase to use a reactive stream (using `asyncio.Queue` and `asyncio.TaskGroup`) to process Dot's action items concurrently rather than sequentially.
*   **Critique:** 
    *   *Pros:* Aligns with the "Dataflow vs. Control Flow" skill learned this cycle; reduces latency in planning.
    *   *Cons:* Over-engineering for a single-agent loop; adds complexity to the `phase_v` state machine.
    *   *Feasibility:* High, but potentially brittle if the state dependencies between tasks are not strictly acyclic.

**Option 2: Observability Tracing for Patch Operations**
*   **Concept:** Implement a correlation ID system in `apply_patch_operations` to track the provenance of every change made to `sam.py` or `workshop_bench/`.
*   **Critique:**
    *   *Pros:* Directly addresses the "State Explosion" and "Observability" weakness identified in the self-correction section. Makes debugging failed patches significantly easier.
    *   *Cons:* Requires modifying the `apply_patch_operations` signature and the `rollback_registry` storage format.
    *   *Feasibility:* High. It is a surgical, high-leverage change that improves long-term maintainability.

**Selection:** Option 2. It directly addresses my self-identified weakness regarding observability in dataflow/patching architectures.

---

## Idea: Patch Provenance Tracing (Correlation IDs)

## Why
Currently, when a patch fails, I have a snapshot of the state, but I lack a clear audit trail of *which* specific Gemini-generated operation caused the drift. By injecting a `correlation_id` into the patch metadata and logging it alongside the file modification, I can trace the lifecycle of a change from the initial prompt to the final state, significantly improving my ability to diagnose "silent" failures.

## Implementation Steps
1.  **Modify `apply_patch_operations`:** Update the function to accept an optional `correlation_id` and log it with every file write.
2.  **Update `_lint_fix_with_gemini` and `_behaviour_fix_with_gemini`:** Generate a unique UUID for each patch batch and pass it to the patcher.
3.  **Update `rollback_registry`:** Include the `correlation_id` in the metadata JSON for each snapshot, allowing me to query which patch caused a specific rollback.
4.  **Log Integration:** Ensure `log.info` captures the `correlation_id` so that `sam.log` becomes a searchable audit trail.

## Risk
*   **Failure Mode:** The `correlation_id` metadata might bloat the `rollback_registry` or cause JSON schema mismatches if not handled with backward compatibility.
*   **Mitigation:** Use a simple `metadata.json` file in the `rollback_registry` that maps `ts` (timestamp) to `correlation_id` rather than modifying the existing `bag_*.json` structure.
*   **Confidence Score:** 9/10. The logic is isolated and does not interfere with the core execution loop.