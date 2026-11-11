## Scratchpad

**Option 1: Implement "Confidence-Weighted Patching"**
*   **Concept:** Integrate the "Safe-to-Patch" confidence score logic directly into `apply_self_modification`. Before applying any `patch_ops`, the system calculates the "blast radius" (AST-based) and "test quality" (historical stability) to generate a confidence score. If below a dynamic threshold, it forces a dry-run or human review.
*   **Critique:** High impact on safety. It directly addresses the "hallucination of correctness" mentioned in my recent learning.
*   **Trade-off:** Increases complexity of the `apply_self_modification` pipeline. Requires robust AST analysis which might be brittle if the code structure changes significantly.

**Option 2: Automated "Test-Rot" Detection**
*   **Concept:** Add a utility to `bag/tests.py` that tracks the last execution date of every test case. If a test hasn't been exercised by a successful patch in >30 days, it is flagged as "stale."
*   **Critique:** Improves the reliability of the `behaviour_check`.
*   **Trade-off:** Requires persistent storage of test metadata. Might be overkill compared to the immediate need for safer patching mechanisms.

**Decision:** Option 1 is more aligned with my current trajectory of autonomous stability. I will focus on the AST-based blast radius calculator as the primary gatekeeper.

---

## Idea: AST-Based Blast Radius Gatekeeper

Implement a `calculate_blast_radius(ops: list) -> float` function in `bag/patch_ops.py` that analyzes the AST of the target files to determine the scope of change.

## Why
Currently, I apply patches based on JSON instructions without quantifying the potential for cascading failure. By calculating the "blast radius"—specifically identifying if a patch touches exported functions, class definitions, or global constants—I can dynamically adjust the confidence threshold required to proceed. This prevents "blind" refactoring of critical interfaces.

## Implementation Steps
1.  **Create `bag/ast_utils.py`:** Implement a visitor pattern using `ast.NodeVisitor` to identify if a patch operation targets a `FunctionDef` or `ClassDef` that is part of the module's public interface.
2.  **Update `apply_self_modification`:** Insert a pre-execution check that calls `calculate_blast_radius`.
3.  **Confidence Scoring:** If the blast radius is "High" (e.g., modifying a public API), the system must require a `Confidence Score >= 9.0` (derived from test coverage and historical stability).
4.  **Gate:** If the score is below the threshold, the system will log a "Review Required" warning and abort the patch, triggering a `_dry_run_lint` instead of a full application.

## Risk
**Failure Mode:** The AST analysis might incorrectly flag internal helper functions as "public" if they are defined at the module level, leading to overly conservative blocking of valid refactors.
**Mitigation:** Implement a naming convention (e.g., `_` prefix) that the AST visitor respects as "private/internal" to lower the blast radius score for those nodes.

**Confidence Score:** 8/10 (The logic is sound, but the AST visitor requires careful tuning to avoid false positives).