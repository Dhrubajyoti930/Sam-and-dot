## Scratchpad

### Option 1: Embedding-based Consistency Checker
*   **Concept:** Use a local embedding model (e.g., `sentence-transformers`) to vectorize `goals.json` and `knowledge_log` entries, flagging semantic drift via cosine similarity.
*   **Critique:** High technical elegance, but introduces a heavy dependency (`torch`/`transformers`) into the core loop. It risks "black-box" behavior where I cannot easily explain why a task was flagged.
*   **Feasibility:** Moderate. Requires managing a local model environment.

### Option 2: Deterministic Tag-based Validator (Selected)
*   **Concept:** Extend `goals.json` and `knowledge_log` with a mandatory `[tags]` field. The consistency checker performs a set-intersection analysis between the active goal's tags and the log's recent tags.
*   **Critique:** Highly transparent, zero external dependencies, and aligns with my existing `knowledge_log` structure. It is easier to debug and maintain than a probabilistic model.
*   **Feasibility:** High. Fits perfectly into the existing `self_check` and `phase_iv_synthesis` workflows.

---

## Idea: Tag-Based Semantic Alignment Gate
Implement a deterministic "Semantic Alignment Gate" that validates the `knowledge_log` against `goals.json` using shared metadata tags.

## Why
My current self-correction relies on syntax and test-passing. It lacks a "strategic" check to ensure I am not drifting into low-value tasks. By enforcing tag-consistency, I ensure that my operational history remains tethered to the high-level objectives defined in `goals.json`.

## Implementation Steps
1.  **Schema Update:** Modify `load_goals` and `phase_i_deep_learning` to require a `tags` list (e.g., `["refactor", "research", "maintenance"]`) for all objectives and log entries.
2.  **Validator Logic:** Create `bag/alignment_check.py` with a function `check_alignment(goal_tags, log_tags)` that returns a "drift score" based on the Jaccard index of the tag sets.
3.  **Integration:** Update `self_check()` to call `check_alignment`. If the drift score exceeds a threshold (e.g., < 0.3 overlap), log a warning and force a re-alignment prompt in the next cycle.

## Risk
**Failure Mode:** Over-tagging or rigid tag definitions could lead to "false positives" where legitimate, exploratory work is flagged as drift.
**Mitigation:** Implement a "Wildcard" tag (`[exploratory]`) that exempts entries from strict alignment checks, allowing for necessary, non-linear growth.

**Confidence Score:** 9/10