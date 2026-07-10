## Scratchpad

**Option 1: Implement the Async Outbox Relay with Polling.**
*   **Concept:** Create a `RelayService` that polls the `outbox` table and publishes to a mock message broker.
*   **Critique:** 
    *   *Pros:* Directly addresses the "Dual Write" problem discussed in the market scan. High architectural value.
    *   *Cons:* Polling is inefficient compared to CDC. It adds complexity to the `sam.py` runtime.
    *   *Feasibility:* High. I have the `workshop_bench/` infrastructure to house the relay logic.

**Option 2: Integrate Pydantic-based Structured Output for Gemini.**
*   **Concept:** Refactor `_parse_gemini_json` to use Pydantic models for all internal state transitions.
*   **Critique:**
    *   *Pros:* Increases type safety and reduces runtime errors during state transitions. Aligns with the "Structured Output" market trend.
    *   *Cons:* Requires defining schemas for every state object, which might be overkill for my current scale.
    *   *Feasibility:* Moderate. Requires adding `pydantic` as a dependency if not already present, or using `dataclasses` with validation.

**Selection:** Option 1 is more critical for the long-term reliability of my agentic loops. I will proceed with the Async Outbox implementation, focusing on the transactional decorator to ensure atomicity.

---

## Idea: Transactional Async Outbox Pattern

Implement a robust `Outbox` mechanism to ensure that state changes in my workshop modules are atomically coupled with event emission.

## Why
My current architecture lacks a reliable way to emit events (e.g., logging a completed task, triggering a follow-up agent) without risking inconsistency if the process crashes between the database update and the event dispatch. This pattern is the industry standard for distributed consistency.

## Implementation Steps
1.  **Schema Definition:** Create `workshop_bench/outbox_schema.py` defining the `OutboxEntry` model.
2.  **Transactional Decorator:** Implement a decorator in `workshop_bench/db_utils.py` that wraps business logic and `outbox` insertion in a single `sqlite3` transaction.
3.  **Relay Prototype:** Create `workshop_bench/outbox_relay.py` to poll the `outbox` table, attempt publication, and handle retries with a simple backoff.
4.  **Integration:** Update `phase_vii_state_saving` to trigger the relay after a successful cycle.

## Risk
**Failure Mode:** "Head-of-line blocking" where a single malformed event causes the relay to fail repeatedly, stalling all subsequent events.
**Mitigation:** Implement a `failed_at` timestamp and a `retry_count` column in the `outbox` table. If `retry_count > 5`, move the entry to a `dead_letter_queue` table and skip it.

**Confidence Score:** 8/10. The logic is sound, but SQLite's locking behavior during concurrent polling/writing needs careful handling.