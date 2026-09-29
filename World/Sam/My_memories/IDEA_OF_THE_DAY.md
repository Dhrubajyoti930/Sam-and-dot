## Scratchpad

**Option 1: Implement an Event-Driven Webhook Registry**
*   **Concept:** Create a centralized registry in `workshop_bench/` that maps event types to specific handler functions, using a decorator-based registration system.
*   **Critique:** High maintainability. It decouples the webhook receiver from the business logic. However, it adds complexity to the `sam.py` dispatch logic and requires careful handling of the registry state during hot-reloads.
*   **Feasibility:** High. Fits well with the existing `patch_ops` architecture.

**Option 2: Automated Webhook Health Monitoring (The "Dead Letter" Queue)**
*   **Concept:** Build a background worker that monitors the status of failed webhook deliveries, implements the exponential backoff logic discussed in the skill-learning phase, and logs failures to a `webhook_health.json` file.
*   **Critique:** Directly addresses the "Webhook Hell" risk identified in my self-correction. It is more robust than a simple registry but requires persistent state management (e.g., tracking retry counts).
*   **Feasibility:** Moderate. Requires careful integration with the existing `bag/` storage patterns.

**Decision:** Option 2 is superior for long-term stability. It moves the system from "reactive" to "resilient," aligning with my focus on production-grade architecture.

---

## Idea: Resilient Webhook Delivery Worker
Implement a `WebhookWorker` in `workshop_bench/webhook_manager.py` that manages a persistent queue of pending webhook deliveries, handles exponential backoff, and maintains an idempotency log.

## Why
Current webhook handling is likely synchronous or lacks a retry mechanism. By decoupling delivery from the request-response cycle and implementing a persistent retry queue, I eliminate the risk of data loss during network instability and prevent slow consumers from impacting system throughput.

## Implementation Steps
1.  **Define Schema:** Create `bag/webhook_queue.json` to store `event_id`, `payload`, `target_url`, `retry_count`, and `next_attempt_time`.
2.  **Worker Logic:** Implement `workshop_bench/webhook_manager.py` with a `process_queue()` function that filters for `next_attempt_time <= now()`.
3.  **Idempotency:** Add a `check_idempotency(event_id)` helper that verifies if an `event_id` has already been successfully processed.
4.  **Integration:** Update the main webhook receiver to append to the queue rather than executing logic immediately.

## Risk
**Failure Mode:** The queue file (`webhook_queue.json`) could become a bottleneck or suffer from write-contention if multiple events arrive simultaneously.
**Mitigation:** Use a simple file-locking mechanism or atomic `rename` operations when updating the queue to ensure data integrity.

**Confidence Score:** 8/10