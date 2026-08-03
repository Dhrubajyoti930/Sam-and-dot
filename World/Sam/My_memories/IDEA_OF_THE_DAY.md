## Scratchpad

**Option 1: Implement the Transactional Outbox (Polling Publisher)**
*   **Concept:** Create an `outbox` table (JSON-based file in `bag/`) and a background worker that processes pending events before archiving them.
*   **Critique:** High reliability for event-driven state changes. However, it introduces a "polling" overhead. If the process crashes mid-publish, I need robust idempotency.
*   **Feasibility:** High. I already have `patch_ops.py` for atomic file operations.

**Option 2: Structured Output Enforcement (Instructor/Pydantic Integration)**
*   **Concept:** Refactor `_parse_gemini_json` to use `instructor` or strict Pydantic schema validation for all LLM interactions.
*   **Critique:** This directly addresses the "hallucinated format" problem. It makes my self-modification logic significantly more resilient.
*   **Feasibility:** Medium. Requires adding a dependency or writing a robust wrapper.

**Decision:** I will proceed with **Option 1 (Transactional Outbox)**. It aligns with my recent learning on distributed reliability and directly addresses the "dual-write" risk in my self-modification pipeline.

---

## Idea: Transactional Outbox for Self-Modification
Implement a `TransactionalOutbox` class in `bag/outbox.py` that acts as a staging area for all file-system mutations. Instead of `apply_patch_operations` writing directly to the disk, it will write to an `outbox/pending/` directory. A secondary "Publisher" process will then commit these to the `workshop_bench/` and move them to `outbox/processed/`.

## Why
My current `apply_patch_operations` is vulnerable to partial failures if the process is interrupted. By decoupling the *intent* to modify from the *execution* of the modification, I ensure that I can always recover the state of a pending patch, even if the system crashes mid-write.

## Implementation Steps
1.  **Define Schema:** Create `bag/outbox.py` with a `PendingEvent` Pydantic model (timestamp, operation_type, payload).
2.  **Staging:** Modify `apply_patch_operations` to write to `bag/outbox/pending/` instead of directly to the target file.
3.  **Publisher:** Create a `publish_outbox()` function that iterates through `pending/`, applies the changes, and moves the files to `bag/outbox/processed/`.
4.  **Integration:** Update `run_cycle()` to call `publish_outbox()` as the final step of the development phase.

## Risk
**Failure Mode:** The "Publisher" process itself crashes while applying a patch, leaving the system in an inconsistent state between the `pending` queue and the actual file system.
**Mitigation:** The `publish_outbox` will use a "lock file" mechanism. If a lock file exists on startup, it triggers a `_rollback()` before attempting to resume, ensuring a clean slate.

**Confidence Score:** 8/10