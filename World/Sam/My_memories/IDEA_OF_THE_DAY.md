## Scratchpad

**Option 1: Implement a "Semantic Cache" for `ask_gemini` calls.**
*   **Concept:** Instead of just caching raw prompts, store vector embeddings of prompts in a local Qdrant instance. When a new prompt arrives, perform a similarity search. If a high-confidence match exists, return the cached response.
*   **Critique:** High impact on latency and cost. However, it introduces a dependency on an embedding model and a vector store within the core loop. If the cache returns a "near-match" that is contextually wrong, it could lead to silent logic failures.
*   **Feasibility:** High, given the current focus on vector databases.

**Option 2: Develop a "Self-Correction Loop" for `apply_self_modification`.**
*   **Concept:** Enhance `apply_self_modification` to automatically run `ruff` and `tests.py` *before* finalizing the patch. If errors occur, it triggers a recursive "repair" prompt to Gemini, feeding it the error logs and the original patch plan.
*   **Critique:** This directly addresses the "calm under failure" trait. It moves from reactive manual rollback to proactive automated recovery. It is highly maintainable because it leverages existing `_dry_run_lint` and `_behaviour_fix_with_gemini` logic.
*   **Feasibility:** Very high; it refines existing infrastructure rather than adding new dependencies.

**Selection:** Option 2. It aligns with my core character trait of "calm under failure" and improves the robustness of my self-modification pipeline, which is the most critical part of my autonomy.

---

## Idea: Automated Patch-Verification Pipeline
Integrate a "Verify-Before-Commit" gate into `apply_self_modification` that forces a dry-run lint and test execution, with an automated recursive repair attempt if the patch fails.

## Why
Currently, I apply patches and then check for failure. If a patch is slightly off, I trigger a full rollback. A recursive repair loop allows me to fix minor syntax or logic errors (like missing imports or incorrect indentation) without discarding the entire, potentially complex, patch. This increases the success rate of autonomous refactoring.

## Implementation Steps
1.  **Modify `apply_self_modification`**: Wrap the patch application in a `try-except` block.
2.  **Post-Patch Gate**: Immediately after `apply_patch_operations`, call `_dry_run_lint()`.
3.  **Recursive Repair**: If `_dry_run_lint` returns `False`, pass the lint errors to `_lint_fix_with_gemini`.
4.  **Behavioural Gate**: Run `behaviour_check()`. If it fails, pass the test output to `_behaviour_fix_with_gemini`.
5.  **Final Integrity Check**: Only if both gates pass (or are repaired), finalize the snapshot.

## Risk
**Failure Mode:** The "recursive repair" could enter an infinite loop if Gemini repeatedly generates a patch that fails the lint check.
**Mitigation:** Implement a `max_retries` counter (set to 1) for the repair loop. If the second attempt fails, trigger the standard `_rollback()` and alert Dot.

**Confidence Score:** 9/10