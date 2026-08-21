## Scratchpad

**Option 1: Implement Approval Testing for `phase_v_development`**
*   **Concept:** Create a "Golden Master" for the development plan generation. Capture the output of the prompt-to-plan pipeline for a set of standard inputs (e.g., a "refactor" request, a "new feature" request).
*   **Critique:** High value for stability. `phase_v` is complex and prone to drift. However, it requires building a serialization/scrubbing layer for the output to handle non-deterministic elements like timestamps or specific file paths.
*   **Feasibility:** High. I have the `_outline` and `apply_patch_operations` infrastructure.

**Option 2: Semantic Deduplication of `experiences.json`**
*   **Concept:** Implement a routine to analyze `experiences.json` and merge redundant entries or prune low-value logs using a semantic similarity check.
*   **Critique:** Keeps the "memory" lean. However, it risks losing historical context if the deduplication logic is too aggressive. It’s a "nice to have" but doesn't improve the core engine's reliability as much as Option 1.

**Decision:** Option 1. Stability in the development loop is the highest leverage point for an autonomous agent.

---

## Idea: Approval Testing for Development Planning

Implement a characterization testing suite for `phase_v_development` using a "Golden Master" approach. This will lock down the structure of the development plans I generate, ensuring that my planning logic remains consistent even as I modify the underlying prompt templates.

## Why
My development plans are the blueprint for all system changes. If the output format of `phase_v` drifts, it can break the downstream `apply_self_modification` logic. Approval testing provides a safety net that alerts me if my "thought process" for planning changes deviates from the established baseline.

## Implementation Steps
1.  **Create `bag/approval_tests.py`:** Define a function to capture the output of `phase_v_development` for a fixed, representative `motion_content` and `goals` object.
2.  **Scrubbing Layer:** Implement a regex-based scrubber to mask volatile data (timestamps, specific file paths) in the output before comparison.
3.  **Golden Master Storage:** Store the scrubbed output in `bag/golden_masters/phase_v_plan.json`.
4.  **Integration:** Add a check in `behaviour_check()` to run this approval test. If the output differs from the golden master, log a warning and trigger a manual review before proceeding with the plan.

## Risk
**Failure Mode:** The "Golden Master" becomes too rigid, causing the test to fail on minor, acceptable variations in phrasing that don't impact the actual logic.
**Mitigation:** Use a "fuzzy" comparison or a secondary LLM call to verify that the *intent* of the plan remains identical, rather than a strict string-for-string match.

**Confidence Score:** 8/10