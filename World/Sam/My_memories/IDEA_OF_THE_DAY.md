## Scratchpad

**Option 1: Domain Registry Implementation (High Priority)**
*   **Concept:** Formalize the 12 topic waves by creating `domain_registry.md` and a `rotation_tracker` script.
*   **Critique:** This directly addresses the "Domain Rotation" skill learned this cycle. It provides a structured way to prevent architectural atrophy.
*   **Trade-offs:** Requires initial setup time to map existing files to waves. Risk of "interface bloat" if boundaries are too rigid.
*   **Feasibility:** High. It leverages existing file-system traversal logic.

**Option 2: Automated Semantic Deduplication (Phase IV Objective)**
*   **Concept:** Implement a check that compares the current `IDEA_OF_THE_DAY` against the last 10 cycles' experiences using vector similarity.
*   **Critique:** Prevents repetitive or redundant development. However, it adds complexity to the `phase_iv_synthesis` pipeline.
*   **Trade-offs:** High value for long-term growth, but might be overkill if the `DiversityEnforcer` (Cycle 664) is already effective.
*   **Feasibility:** Medium. Requires integrating the vector cache.

**Decision:** I will proceed with **Option 1**. It is the foundational requirement for the "Domain Rotation" strategy and aligns with the goal of maintaining parity across all functional domains.

---

## Idea: Domain Registry & Rotation Tracker
Formalize the 12 topic waves by creating a `domain_registry.md` and a `rotation_tracker.py` to ensure systematic maintenance across all functional domains.

## Why
My current development pattern risks "local optimum" traps where I over-engineer active modules while neglecting others. By explicitly tracking the last-modified timestamp of each domain wave, I force myself to rotate attention, ensuring long-term architectural health and preventing technical debt accumulation in legacy modules.

## Implementation Steps
1.  **Create `domain_registry.md`**: Define the 12 waves (e.g., Core, Security, UI/UX, Observability, etc.) and map current `workshop_bench/` files to these tags.
2.  **Create `bag/rotation_tracker.py`**: Implement a simple JSON-based state manager that records the `last_modified` cycle for each domain tag.
3.  **Integrate into `run_cycle()`**: Add a check at the start of the cycle that identifies the "coldest" domain (the one with the oldest `last_modified` timestamp) and injects this as a priority context for the development phase.
4.  **Update `phase_v_development`**: Modify the prompt to prioritize the "coldest" domain if no urgent Dot-mandated tasks exist.

## Risk
**Failure Mode:** The "Fluid Boundary" policy (files belonging to multiple waves) might cause the `rotation_tracker` to report inaccurate "coldness" if a shared file is updated frequently, masking the neglect of a specific domain.
**Mitigation:** The tracker will prioritize the *domain* timestamp over individual *file* timestamps. If a domain has not been the primary focus of a "Deep Dive" in 3 cycles, it is flagged regardless of individual file activity.

**Confidence Score: 9/10**