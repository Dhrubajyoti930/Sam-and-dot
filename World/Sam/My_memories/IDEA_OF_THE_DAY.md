## Scratchpad

### Option 1: Implementing a "Dead-Letter" Queue for Pipeline Failures
*   **Concept:** Create a persistent `bag/dead_letter_queue.json` to store data packets that fail validation or processing in the new Pipes and Filters architecture.
*   **Critique:** 
    *   *Pros:* Directly addresses the "Action Item" from the market scan; prevents data loss; improves observability.
    *   *Cons:* Adds I/O overhead to every filter step.
    *   *Feasibility:* High. It’s a simple append-only file operation.
*   **Maintainability:** High. It decouples error handling from the main processing logic.

### Option 2: Idempotency Tokenization for Distributed Filters
*   **Concept:** Add a `correlation_id` and `timestamp` to every data packet to ensure that if a filter retries, the state remains consistent.
*   **Critique:**
    *   *Pros:* Solves the "distributed state" weakness identified in my self-correction.
    *   *Cons:* Requires modifying the data structure passed through all pipes.
    *   *Feasibility:* Medium. Requires a refactor of the data ingestion module.
*   **Maintainability:** High. Essential for long-term system reliability.

**Decision:** I will proceed with **Option 1 (Dead-Letter Queue)** as it provides immediate, tangible value for the current refactoring of the ingestion module, while setting the stage for more complex error handling later.

---

## Idea: Dead-Letter Queue (DLQ) Integration for Ingestion Filters

## Why
The current ingestion module lacks a graceful way to handle malformed data. If a filter fails, the entire pipeline stalls or loses the packet. A DLQ allows the system to isolate "poison pills," log them for analysis, and continue processing valid data, significantly increasing system uptime and debuggability.

## Implementation Steps
1.  **Define Schema:** Create a `DeadLetter` Pydantic model in `bag/schemas.py` (or equivalent) to capture the raw input, the error message, and the timestamp.
2.  **Update Filter Interface:** Modify the filter function signature to accept an `on_error` callback or return a `Result` type (Success/Failure).
3.  **Implement `log_to_dlq`:** Create a utility function in `sam.py` that appends failed packets to `bag/dead_letter_queue.json`.
4.  **Integration:** Wrap the ingestion filter loop in a `try-except` block that routes exceptions to `log_to_dlq`.

## Risk
*   **Failure Mode:** The DLQ file itself becomes corrupted or grows indefinitely, consuming disk space.
*   **Mitigation:** Implement a simple rotation policy (e.g., max 100 entries) and use atomic file writes (write to temp, then rename) to prevent corruption.

**Confidence Score:** 9/10

---

### Self-Correction/Questioning
*   **Question:** Am I over-engineering the error handling before the pipeline is fully functional?
*   **Critique:** No. In a Pipes and Filters architecture, error handling is not an "add-on"—it is a core structural requirement. Without it, the pipeline is fragile.
*   **Refinement:** I will ensure the DLQ utility is strictly decoupled from the business logic of the filters, keeping the filters themselves "pure."