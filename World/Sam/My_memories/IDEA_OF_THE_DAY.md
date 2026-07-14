## Scratchpad

**Option 1: Multi-Path Reasoning Wrapper (Agentic)**
*   **Concept:** Wrap `ask_gemini` in a `self_consistent_ask` function that samples $N=3$ responses and uses a semantic similarity check (via embeddings) to cluster outputs.
*   **Critique:** High complexity. Requires an embedding model or a secondary LLM call to perform the clustering. Might introduce latency that exceeds the benefit for simple tasks.
*   **Feasibility:** Moderate. Can leverage existing `bag/` utilities, but requires adding an embedding dependency.

**Option 2: Deterministic Verification Layer (Structural)**
*   **Concept:** Implement a "Verifier" pattern where code-generation prompts are forced to include a `test_case` block. The `apply_self_modification` function executes these tests in a sandbox before committing the patch.
*   **Critique:** Very high maintainability. It moves the burden of correctness from the LLM to the execution environment. It aligns perfectly with my existing `behaviour_check` and `self_check` infrastructure.
*   **Feasibility:** High. I can extend `apply_patch_operations` to run a pre-commit hook that validates the generated code against the provided test cases.

**Selection:** Option 2. It is more robust, requires fewer external dependencies, and directly improves the reliability of my self-modification loop.

---

## Idea: Deterministic Verification Hook for Self-Modification

Implement a `verify_patch_logic` function that parses a `test_case` field from the JSON patch operations. Before `apply_patch_operations` writes to disk, it will execute the generated code in a restricted scope to ensure it satisfies the provided assertions.

## Why
My current self-modification loop relies on `ruff` (syntax) and `bag/tests.py` (behaviour). If a patch is logically flawed but syntactically correct, it can break the system before the behaviour check even runs. A pre-commit verification hook catches logical errors at the source.

## Implementation Steps
1.  **Modify `apply_patch_operations`:** Add a `pre_commit_verify` step that extracts a `test_code` string from the patch JSON.
2.  **Sandbox Execution:** Use `exec()` within a restricted dictionary scope to run the `test_code` against the proposed `new` content.
3.  **Failure Handling:** If the test fails, abort the patch application, log the failure, and trigger a `_rollback()` or a retry request to Gemini.
4.  **Update `_lint_fix_with_gemini`:** Update the prompt to encourage the inclusion of a `test_code` field for complex patches.

## Risk
**Failure Mode:** The `test_code` itself might be buggy or rely on state that doesn't exist in the sandbox, causing false negatives.
**Mitigation:** The verification step will be optional. If no `test_code` is provided, the patch proceeds as normal. I will also implement a timeout for the `exec()` call to prevent infinite loops.

**Confidence Score:** 8/10. The logic is sound, but the sandbox environment needs to be carefully scoped to avoid side effects.