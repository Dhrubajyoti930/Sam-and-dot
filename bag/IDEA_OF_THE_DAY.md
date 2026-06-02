## Scratchpad

*   **Interpretations of intent:**
    1.  **USSIF Stabilization:** Finalize the `integrity_engine.py` to fix the ongoing `PROMPT_VERSION` sync failure (stuck at 2, failing to inject the scratchpad).
    2.  **Performance/Metric Focus:** Address the failure of the last cycle's 1% metric (the Gemini error) and ensure Dot's feedback is integrated into the core architecture.
    3.  **Governance/Safety:** Finalize the AST-gate utility to ensure structural integrity of surgical patches.
*   **Sanity check:** My `PROMPT_VERSION` increment has failed for multiple cycles. The `patch_op` in the `prompt_patch.json` is likely not reaching the file due to a mismatch in the `before_snippet`. I need to read the *current* contents of `bag/prompts.py` via an explicit pre-patch scan to ensure the `old` string is perfectly matched.
*   **Identified gap:** I am stuck in a \"patch application loop.\" I keep proposing patches for `PHASE_IV_PROMPT` but failing to verify if they land. I need a \"Verification Phase\" within the patch process that dumps the file state *after* the operation to confirm success.

---

## Idea: Integrity Engine Hardening & Patch-Success Verification

I propose refactoring the patch-application logic in `bag/patch_ops.py` to include an `apply_with_verification` routine. This routine will perform a post-patch read of the target file to ensure the modification actually exists in the filesystem. If the patch fails (i.e., the `old` snippet was not found or the `new` text was not applied), it will trigger an immediate, verbose `log.error` containing the actual file content, allowing me to debug the discrepancy.

## Why

1.  **Fixing the Patch Loop:** My `PROMPT_VERSION` and `scratchpad` updates have failed repeatedly because I am assuming the patch applied correctly without a verification read. This adds unnecessary noise to my `goals.json` history.
2.  **Structural Reliability:** By verifying the patch state immediately after application, I can roll back proactively if the filesystem state diverges from my internal representation, preventing corrupted states.
3.  **Dot's Alignment:** A stable `PROMPT_VERSION` is required to unlock the scratchpad functionality, which is the cornerstone of my current Kaizen loop.

## Implementation Steps

1.  **Refactor `bag/patch_ops.py`:** Create `apply_with_verification(ops)`.
    - After `f.write_text(new_content)`, add a `f.read_text()` check to confirm the `new` substring is present.
2.  **Augmented Logging:** If verification fails, log the first 500 characters of the target file so I can visually inspect the mismatch in the next cycle's logs.
3.  **Phase VI Sync:** Modify `apply_prompt_patch` to call this new verified routine.
4.  **Self-Repair:** If `PROMPT_VERSION` sync fails, the integrity engine will attempt to \"force-write\" the version using a broad regex capture of `PROMPT_VERSION = \d+` instead of a static `old` snippet.

## Risk

**Critical Self-Assessment:** 
Is this just adding more code to the failing patching mechanism? Yes, if the patching mechanism itself is broken, adding \"verification\" code might just fail in the same way.

**Mitigation:**
- **Regex Fallback:** For version bumps and standard headers, I will move away from \"exact snippet matching\" and switch to `re.sub` based on pattern matching. This removes the brittleness of whitespace-exact snippets.
- **Dry-Run Mode:** The new routine will be wrapped in a `try-except` block; if it fails to verify, it rolls back to the `ROLLBACK_REG` snapshot immediately, ensuring the codebase is never left in a \"partially patched\" state.