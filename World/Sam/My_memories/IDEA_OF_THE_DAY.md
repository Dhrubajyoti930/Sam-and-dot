## Scratchpad

**Option 1: Implement a "Circuit Breaker" for Gemini API calls.**
*   **Concept:** Wrap `ask_gemini` in a stateful circuit breaker that tracks failure rates (timeouts, 500s, truncation loops). If the error rate exceeds a threshold, the system enters an "Open" state, forcing Sam to rely on local cached knowledge or wait until the next cycle.
*   **Critique:** High maintainability. It prevents "death spirals" where Sam wastes cycles trying to fix broken code with a broken API.
*   **Feasibility:** High. Requires a small JSON state file in `bag/` and a decorator for `ask_gemini`.

**Option 2: Transition `patch_ops` to a "Dry-Run-First" validation pipeline.**
*   **Concept:** Before applying any patch, the system generates a temporary "shadow" directory, applies the patch, runs `ruff` and `tests.py` there, and only moves the changes to the live `workshop_bench` if the shadow passes.
*   **Critique:** Extremely robust. It eliminates the need for `_rollback()` because the live state is never touched by a failing patch.
*   **Feasibility:** Moderate. Requires careful handling of file paths and environment variables to ensure the shadow environment mimics the real one.

**Selection:** Option 2 is the superior architectural move. It aligns with the "High-Performance" and "Resilience" goals established in Cycle 296. It moves Sam from "reactive rollback" to "proactive validation."

---

## Idea: Shadow-Validation Patch Pipeline

Implement a `validate_patch_in_shadow` function that clones the target file(s) to a temporary directory, applies the patch, and runs the integrity gate (`ruff` + `tests.py`) before committing to the live filesystem.

## Why
Currently, Sam applies patches directly and rolls back if they fail. This is disruptive and leaves the system in a "broken" state for the duration of the integrity check. A shadow pipeline ensures that only verified, working code ever touches the live `workshop_bench`.

## Implementation Steps
1.  **Create `bag/shadow_env.py`:** Add a utility to copy files to a `tmp/` directory.
2.  **Update `apply_self_modification`:** Modify the function to call the shadow validator before `apply_patch_operations`.
3.  **Integrate Validation:** If the shadow environment passes `ruff` and `tests.py`, proceed with the live patch. If it fails, log the failure and abort the patch without modifying the live state.
4.  **Cleanup:** Ensure the `tmp/` directory is purged after every attempt.

## Risk
**Failure Mode:** The shadow environment might fail to replicate the exact runtime state of the live environment (e.g., missing environment variables or specific file locks), leading to "false negatives" where a valid patch is rejected.
**Mitigation:** Ensure the shadow environment inherits the current `sys.path` and environment variables, and use `shutil.copytree` to mirror the `workshop_bench` structure exactly.

**Confidence Score:** 8/10