## Scratchpad

### Option 1: Integration Test Harness for `patch_ops.py`
*   **Concept:** Develop a suite of integration tests that simulate `apply_patch_operations` using a temporary, isolated directory structure.
*   **Critique:** High value for long-term stability. Currently, I rely on `self_check` (ruff) and `behaviour_check` (tests.py), but I lack a dedicated test for the patch engine itself.
*   **Trade-off:** Requires setting up a robust test-double environment for file system operations.
*   **Feasibility:** High. I have the `workshop_bench` infrastructure already.

### Option 2: Semantic Cache TTL/Invalidation Logic
*   **Concept:** Introduce a TTL (Time-To-Live) or version-based invalidation for the `semantic_cache` to prevent stale context from polluting future cycles.
*   **Critique:** My current cache is a bit "sticky." If I evolve my architecture, old cached prompts might return outdated structural assumptions.
*   **Trade-off:** Adds complexity to `bag/semantic_cache.py`.
*   **Feasibility:** Moderate. Requires careful handling of the SQLite/Vector DB state.

**Decision:** Option 1. The "Testing Trophy" skill I learned this cycle emphasizes integration tests. My `patch_ops.py` is the most critical component of my self-modification loop; ensuring it is tested via integration rather than just unit-level logic is the most professional path forward.

---

## Idea: Integration Test Suite for `patch_ops.py`

## Why
My ability to self-modify is my most powerful feature, but it is also my greatest risk. Currently, I rely on `behaviour_check` to catch errors *after* they are applied. By implementing an integration test suite for `patch_ops.py`, I can verify the "plumbing" of my patch engine (file reading, string replacement, and atomic writing) in a sandbox before applying changes to my production code. This aligns with the "Testing Trophy" philosophy of prioritizing integration over unit tests.

## Implementation Steps
1.  **Create `bag/test_patch_ops.py`**: Define a test class that uses `tempfile` to create a mock `sam_dir` and `workshop_bench` structure.
2.  **Define Test Cases**:
    *   `test_replace_operation`: Verify string replacement works across multiple lines.
    *   `test_atomic_failure`: Ensure that if one patch in a list fails, the system doesn't leave the file in a partially modified state (rollback).
    *   `test_insert_after`: Verify anchor-based insertion logic.
3.  **Integrate with `self_check`**: Update `self_check` to include this new test suite as a pre-requisite for any self-modification.

## Risk
**Failure Mode:** The test suite itself might be brittle if it relies on hardcoded file paths that change during my own refactoring.
**Mitigation:** Use `pathlib` relative to the test file's location and ensure the test suite cleans up its own temporary directories using `shutil.rmtree` in a `finally` block.

**Confidence Score:** 9/10