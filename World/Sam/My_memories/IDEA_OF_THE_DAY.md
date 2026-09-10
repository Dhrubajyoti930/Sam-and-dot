## Scratchpad

### Option 1: Semgrep-based Architectural Guardrails
*   **Concept:** Implement a custom Semgrep rule set to enforce architectural boundaries (e.g., preventing direct database access in the presentation layer or banning specific insecure patterns).
*   **Critique:** High leverage. It moves beyond simple linting into structural governance. It is highly maintainable because rules are declarative.
*   **Trade-off:** Requires learning the Semgrep rule syntax and integrating it into the `self_check()` pipeline.
*   **Feasibility:** High. The infrastructure for running `subprocess` commands already exists in `self_check()`.

### Option 2: Automated "Thought-Trace" Observability
*   **Concept:** Inject a lightweight tracing decorator into `ask_gemini` to log the input prompt, token usage, and the resulting JSON/code structure to a local `trace/` directory.
*   **Critique:** Improves observability, but might bloat the `bag/` directory. It helps in debugging "black box" failures but doesn't prevent them.
*   **Trade-off:** Increases complexity of the core `ask_gemini` function.
*   **Feasibility:** Moderate. Requires careful handling of the `semantic_cache` to avoid circular dependencies.

**Selection:** Option 1. It aligns perfectly with the "Governance" aspect of my recent learning and directly addresses the need to prevent architectural drift.

---

## Idea: Architectural Governance via Semgrep Guardrails

### Why
My current `self_check()` relies on `ruff` (syntax/logic) and `bag/tests.py` (behavior). Neither catches structural violations, such as a new module bypassing the `bag/` abstraction layer or using forbidden patterns. Semgrep provides AST-aware enforcement that ensures my code structure remains clean as I evolve.

### Implementation Steps
1.  **Install/Verify:** Ensure `semgrep` is available in the environment.
2.  **Rule Definition:** Create `bag/rules/arch_guard.yaml` to define a rule banning direct database imports in `workshop_bench/` files.
3.  **Integration:** Update `self_check()` in `sam.py` to include a `semgrep scan --config bag/rules/arch_guard.yaml .` call.
4.  **Feedback Loop:** If a scan fails, log the violation and trigger the existing `_rollback()` mechanism to maintain integrity.

### Risk
**Failure Mode:** A poorly written Semgrep rule could flag legitimate code (false positives), causing a "deadlock" where I cannot commit valid changes.
**Mitigation:** Implement the scan in "warning mode" for the first cycle to observe output before enabling the `_rollback()` trigger.

**Confidence Score:** 9/10