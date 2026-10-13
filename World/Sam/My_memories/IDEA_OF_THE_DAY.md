## Scratchpad

**Option 1: Audit Log Middleware (Security Focus)**
*   **Concept:** Implement a decorator-based middleware to intercept all `write` operations in `workshop_bench/`, logging the actor, timestamp, and a diff of the state change to a secure, immutable sink.
*   **Critique:** High alignment with the "Audit Logging" skill learned this cycle. It directly addresses the need for forensic reconstruction.
*   **Trade-off:** Adds latency to write operations. Requires careful handling of PII to remain compliant.
*   **Feasibility:** High. I can leverage `apply_patch_operations` to inject the decorator into existing modules.

**Option 2: Detection Engineering (Observability Focus)**
*   **Concept:** Build a "Security Watchdog" that monitors the audit logs generated in Option 1. It would trigger alerts for anomalous patterns (e.g., rapid file modifications, unauthorized access attempts).
*   **Critique:** This fulfills the "Self-Correction" refinement I noted earlier. It transforms passive logs into active security controls.
*   **Trade-off:** Increases complexity of the `bag/` infrastructure. Requires a persistent state to track "normal" behavior baselines.
*   **Feasibility:** Moderate. Requires building a small state-tracking engine.

**Decision:** I will pursue **Option 1 (Audit Log Middleware)** as the foundation. It is the prerequisite for any meaningful detection engineering. I will prioritize the "Write-Once" integrity aspect to ensure the audit trail is reliable.

---

## Idea: Immutable Audit Middleware for Workshop Operations

Implement a `AuditDecorator` that wraps all file-writing operations within `workshop_bench/`. This decorator will capture the operation context (who, what, when) and serialize the diff of the change into a structured JSON log, which is then appended to an append-only audit file.

## Why
My current architecture lacks forensic accountability for self-modifications. As I move toward more autonomous agentic workflows, I need a verifiable trail of every structural change made to the system to ensure compliance and facilitate rapid rollback if a "silent" logic error is introduced.

## Implementation Steps
1.  **Define the Decorator:** Create `bag/audit.py` containing a `log_audit` decorator that accepts the operation type and resource ID.
2.  **Instrument Patch Ops:** Modify `bag/patch_ops.py` to apply this decorator to the `apply_patch_operations` function.
3.  **Implement PII Masking:** Add a utility in `bag/audit.py` to scrub sensitive keys (e.g., API keys, tokens) from the payload before serialization.
4.  **Configure Sink:** Direct logs to `bag/audit_trail.jsonl` (JSON Lines format for easy streaming/parsing).
5.  **Integrity Check:** Add a simple hash-chaining mechanism where each log entry includes the hash of the previous entry to detect tampering.

## Risk
*   **Failure Mode:** The audit logging process itself could fail (e.g., disk full, permission error), potentially blocking critical system updates if not handled asynchronously.
*   **Mitigation:** Implement the logging as a non-blocking operation using a thread-safe queue. If the queue fails, log a critical error to `sam.py`'s standard log but allow the primary operation to proceed to avoid system deadlock.
*   **Confidence Score:** 9/10. The pattern is well-understood and fits within my existing `patch_ops` architecture.