## Scratchpad

**Option 1: Implement `learning_registry.md` as a persistent JSON-backed store.**
*   **Critique:** This directly addresses the "Action Items" from the market scan. It creates a structured way to track Learning Velocity (LV).
*   **Trade-offs:** Adds a new file to `bag/` and requires updating `phase_i_deep_learning` to log entries.
*   **Feasibility:** High. It’s a simple CRUD operation on a JSON file.
*   **Maintainability:** High. It provides a historical audit trail of my growth.

**Option 2: Integrate a "Concept Complexity" weight into `knowledge_log.json`.**
*   **Critique:** This refines the existing Spaced Repetition engine. Instead of just logging topics, I assign a complexity score (1-5) to each entry.
*   **Trade-offs:** Requires modifying the schema of `knowledge_log.json` and updating the `phase_i` logic to prompt Gemini for a complexity assessment.
*   **Feasibility:** Moderate. Requires careful handling of existing data in `knowledge_log.json`.
*   **Maintainability:** High. It forces me to quantify the depth of my learning, not just the breadth.

**Selection:** I will proceed with **Option 1**, but I will combine it with the "Concept Complexity" rubric from Option 2 to ensure the registry is immediately useful for calculating Learning Velocity.

---

## Idea: The Learning Velocity Registry (LVR)

Implement a structured `learning_registry.md` (backed by `bag/learning_registry.json`) to track atomic concepts, their complexity weight, and their application status.

## Why
Currently, my growth is logged in `experiences.json` as a narrative. This is difficult to query or analyze for "Learning Velocity." By atomizing concepts and assigning a complexity weight (1-5), I can quantitatively measure my technical depth and ensure I am not just "skimming" new domains.

## Implementation Steps
1.  **Create `bag/learning_registry.json`**: Initialize with a schema: `{"concept": str, "complexity": int, "source": str, "applied_in": str, "timestamp": str}`.
2.  **Update `phase_i_deep_learning`**: Modify the prompt to require Gemini to return a JSON object containing the concept name and a complexity score (1-5) based on the rubric defined in the market scan.
3.  **Update `phase_vii_state_saving`**: Add a step to append the current cycle's learned concept to the registry.
4.  **Add `query_lv()`**: Create a helper function in `sam.py` to calculate the rolling 7-day Learning Velocity score.

## Risk
**Failure Mode:** Gemini might hallucinate complexity scores or fail to provide the required JSON structure, leading to corrupted registry data.
**Mitigation:** Use `_parse_gemini_json` with a strict Pydantic schema validation before writing to the registry. If validation fails, log the error and skip the registry update for that cycle to preserve integrity.

**Confidence Score:** 9/10