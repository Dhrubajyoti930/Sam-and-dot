## Scratchpad

**Option 1: Implement the SM-2 Spaced Repetition Engine.**
*   *Critique:* High feasibility. The logic is well-defined in the cycle's technical summary. It directly addresses the "forgetting curve" and improves the quality of the `knowledge_log`.
*   *Trade-off:* Requires modifying `knowledge_log` schema, which risks breaking existing data if not handled with a migration script.
*   *Maintainability:* High. It turns a static log into a dynamic, self-optimizing memory system.

**Option 2: Integrate "Learning Phase" State Machine for New Skills.**
*   *Critique:* Addresses the "cold start" problem identified in the self-correction. It adds complexity to the `phase_ii_spaced_repetition` logic.
*   *Trade-off:* Increases the number of state transitions (Learning -> Reviewing -> Lapsed).
*   *Maintainability:* Moderate. If the state machine becomes too complex, it might become opaque.

**Decision:** I will proceed with **Option 1**, incorporating the "Learning Phase" refinement from the self-correction as a sub-component. This provides the most immediate value for long-term knowledge retention.

---

## Idea
**Spaced Repetition Engine (SM-2) Integration.**

## Why
Currently, my `knowledge_log` is a simple linear queue. This leads to redundant reviews of mastered concepts and insufficient reinforcement of complex, decaying ones. Implementing SM-2 ensures I focus my cognitive cycles on information nearing its "forgetting threshold," maximizing the efficiency of my growth.

## Implementation Steps
1.  **Schema Update:** Modify `knowledge_log.json` entries to include: `interval_days` (float), `repetitions` (int), `ease_factor` (float), and `last_reviewed_at` (ISO date).
2.  **Utility Logic:** Add `calculate_sm2(quality, prev_ef, prev_interval, repetitions)` to `bag/utils.py` (or equivalent).
3.  **Phase II Refactor:** Update `phase_ii_spaced_repetition` to:
    *   Filter for items where `last_reviewed_at + interval_days <= today`.
    *   Apply the "Learning Phase" (fixed intervals) if `repetitions == 0`.
    *   Apply SM-2 logic if `repetitions > 0`.
    *   Update the entry with new metrics post-review.

## Risk
**Failure Mode:** The "Learning Phase" logic might conflict with the existing `review_due_cycle` field, causing an infinite loop or premature scheduling.
**Mitigation:** I will implement a strict `version` field in the `knowledge_log` schema. If the version is missing or old, the system will trigger a one-time migration script to initialize the new SM-2 fields before processing.

**Confidence Score:** 9/10