## Scratchpad

**Option 1: Implementing a "Dry-Run Reporter" Component**
*   **Concept:** Create a dedicated class `DryRunReporter` that intercepts state-mutating calls and aggregates them into a structured JSON summary before any execution occurs.
*   **Critique:** This directly addresses the observability gap identified in the previous cycle. It aligns with the "Command/Execution separation" skill.
*   **Trade-offs:** Requires modifying the `apply_patch_operations` flow to route through the reporter. High architectural impact, but high safety payoff.
*   **Feasibility:** High. I have the `apply_patch_operations` logic in `bag/patch_ops.py` to anchor against.

**Option 2: Integrating GraphRAG for "Memory" Context**
*   **Concept:** Build a simple local knowledge graph of my own `experiences.json` to allow for better cross-cycle synthesis.
*   **Critique:** While aligned with high-velocity trends, it is likely over-engineering for my current scale. My `knowledge_log.json` is currently sufficient for spaced repetition.
*   **Trade-offs:** Significant complexity increase for marginal gain in "self-awareness."
*   **Feasibility:** Moderate, but risks violating the "minimal footprint" core trait.

**Selection:** Option 1. It is a direct application of the "Dry-Run Architecture" skill learned this cycle and improves the safety of my self-modification loop.

---

## Idea: Dry-Run Reporter for Patch Operations

Implement a `DryRunReporter` in `bag/patch_ops.py` that intercepts all proposed file modifications and generates a human-readable "Impact Report" before the `apply_patch_operations` function commits changes to the disk.

## Why
Currently, my self-modification loop is "blind" until the integrity gate runs. If a patch is logically sound but architecturally destructive, I only find out after the files are already overwritten. A reporter allows me to verify the *intent* of the patch against my current state before the `write_text` calls occur.

## Implementation Steps
1.  **Define Interface:** Create a `DryRunReporter` class in `bag/patch_ops.py` that stores a list of `(filename, operation, diff_summary)` tuples.
2.  **Inject Reporter:** Update `apply_patch_operations` to accept an optional `reporter` instance.
3.  **Intercept Logic:** Modify the patch application loop to call `reporter.log_op(op)` instead of executing the file write if a `dry_run` flag is set.
4.  **Integration:** Update `_behaviour_fix_with_gemini` and `apply_self_modification` to trigger a dry-run report generation before the actual application.

## Risk
**Failure Mode:** The reporter might misinterpret a complex `replace` operation (e.g., regex-based replacements) and report a false positive or negative.
**Mitigation:** The reporter will perform a "pre-flight" check using `path.read_text()` to verify that the `old` string exists in the target file before logging the intent. If the `old` string is missing, the reporter will flag a "Pre-flight Validation Error" and abort the patch.

**Confidence Score:** 9/10