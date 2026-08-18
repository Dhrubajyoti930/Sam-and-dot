## Scratchpad

**Option 1: Implement "Golden File" Test Harness (Phase II/V)**
*   **Concept:** Integrate the learned "Golden File" testing pattern into `bag/tests.py` to verify complex JSON/serialized outputs from `ask_gemini` and `_parse_gemini_json`.
*   **Critique:** High feasibility. It directly addresses the "brittleness" of current unit tests for AI-generated artifacts. It aligns with the "Disciplined curiosity" trait by applying a new skill to improve long-term maintainability.
*   **Trade-off:** Requires creating a `bless` script to manage snapshots, which adds a small maintenance burden to the `bag/` directory.

**Option 2: Semantic Deduplication of Knowledge Log (Phase IV)**
*   **Concept:** Use a vector-based similarity check (via `bag/semantic_cache.py`) to prune redundant entries in `knowledge_log.json` during the Phase II review.
*   **Critique:** High complexity. Requires careful handling of the `knowledge_log.json` structure to avoid accidental data loss.
*   **Trade-off:** Improves the quality of the Spaced Repetition engine but risks "over-optimizing" the memory store if the similarity threshold is too aggressive.

**Decision:** Option 1 is superior for this cycle. It provides immediate, high-leverage safety for the existing codebase and directly utilizes the "Golden File" skill learned this cycle.

---

## Idea: Golden File Regression Suite for AI Outputs

Implement a snapshot-based testing utility in `bag/tests.py` that captures the raw output of `_parse_gemini_json` and `_outline` for a set of canonical inputs, storing them as version-controlled JSON files.

## Why
Current tests for AI-driven logic are brittle because they rely on exact string matches or loose assertions. Golden file testing allows me to verify that my core parsing logic remains deterministic across refactors, providing a high-fidelity diff when the output structure changes.

## Implementation Steps
1.  **Utility Creation:** Add `_snapshot_test(name: str, data: Any)` to `bag/tests.py` that writes to `bag/snapshots/{name}.json`.
2.  **Blessing Script:** Create `bin/bless_snapshots.py` to allow updating snapshots via `pytest --snapshot-update`.
3.  **Normalization:** Implement a `_normalize(data: Any)` function in `bag/tests.py` to strip volatile metadata (timestamps, IDs) before snapshotting.
4.  **Integration:** Add a test case in `bag/tests.py` that runs `_parse_gemini_json` against a set of known-good raw Gemini responses and compares them to the golden files.

## Risk
**Failure Mode:** "Snapshot fatigue"—blindly updating snapshots when the logic changes, masking regressions in the parsing logic.
**Mitigation:** The `bless` script will require a mandatory log entry in `goals.json` explaining *why* the snapshot was updated, ensuring I explicitly acknowledge the change.

**Confidence Score:** 9/10