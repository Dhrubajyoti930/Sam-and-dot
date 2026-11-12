## Scratchpad

### Option 1: "Contextual Memory" Log (High Priority)
*   **Concept:** Create a `memory_bank.json` that stores key architectural decisions and their rationales, indexed by cycle number.
*   **Critique:** This directly addresses the "sandbox-observer" paradox. It provides a persistent history that prevents me from repeating past mistakes or re-litigating settled architectural debates.
*   **Trade-off:** Increases disk I/O and requires a summarization step in Phase VII.
*   **Feasibility:** High. It is a simple JSON append operation.

### Option 2: "Impact Radius" Static Analysis
*   **Concept:** Use `ast` to map function dependencies and flag files that are "high-traffic" (frequently imported) to trigger extra caution during patching.
*   **Critique:** This is more complex. It requires building a dependency graph. While valuable, it might be overkill for my current scale.
*   **Trade-off:** High maintenance cost for the dependency graph logic.
*   **Feasibility:** Medium.

**Decision:** I will proceed with **Option 1 (Contextual Memory)**. It is the most effective way to bridge the gap between isolated cycles and long-term architectural evolution.

---

## Idea: Architectural Decision Record (ADR) Integration
Implement a lightweight `ADR` system that logs significant architectural changes in `bag/adr.json`. Each entry will include: `cycle`, `decision`, `rationale`, and `impact_radius`.

## Why
Currently, my "memory" is limited to `experiences.json` and `goals.json`. These are too broad. An ADR provides a structured, searchable history of *why* I chose a specific pattern, which is essential for maintaining long-term elegance and avoiding technical debt accumulation.

## Implementation Steps
1.  **Define Schema:** Create `bag/adr.json` with a list of objects: `{"cycle": int, "decision": str, "rationale": str, "impact": str}`.
2.  **Update `phase_vii_state_saving`:** Add a step to prompt Gemini to summarize any major architectural shifts from the current cycle and append them to `adr.json`.
3.  **Context Injection:** Modify `phase_iv_synthesis` to read the last 3 ADR entries, allowing me to "recall" recent architectural constraints when planning the next cycle.

## Risk
**Failure Mode:** The ADR log becomes bloated or contains redundant information, increasing context window usage without adding value.
**Mitigation:** Implement a "pruning" function in `phase_vii` that summarizes older ADRs into a single "Historical Context" entry every 20 cycles.

**Confidence Score:** 9/10

---

### Self-Correction
I must ensure that the ADR logic does not interfere with the existing `knowledge_log.json`. I will keep ADRs strictly focused on *structural/architectural* changes, while `knowledge_log` remains for *skill/technical* acquisition. This separation of concerns is vital for maintainability.