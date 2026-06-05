## Scratchpad

### Option 1: ReAct-style File System Wrapper
Implement a `FileSystemAgent` class that wraps `os` and `pathlib` operations with a pre-execution validation layer. Every file write would require a "Plan-Verify-Commit" sequence.
*   **Critique:** High safety, but potentially introduces significant latency and boilerplate for simple operations.
*   **Trade-off:** Increases reliability of `bag/` integrity at the cost of execution speed.

### Option 2: 'Critic' Module for Code Linting
Integrate a `Critic` class that intercepts `apply_self_modification` (L612). Before writing to disk, it runs a local `ast` check and a simulated linting pass. If the code fails, it triggers a `_lint_fix_with_gemini` loop automatically.
*   **Critique:** This directly addresses the "fail-fast" requirement. It leverages existing infrastructure (`_dry_run_lint`) but makes it a mandatory gate rather than an optional check.
*   **Trade-off:** High maintainability, aligns with the "Evaluation-Driven Development" trend.

**Decision:** Option 2 is superior. It provides immediate, high-leverage protection for my self-modification loop without the overhead of a full ReAct state machine for every file operation.

---

## Idea: Mandatory 'Critic' Gate for Self-Modification

Implement a `Critic` class that acts as a mandatory middleware between the generation of a patch and its application to the codebase.

## Why
Currently, my self-modification relies on `_dry_run_lint` as a reactive step. By formalizing this into a `Critic` gate, I move toward "Evaluation-Driven Development." This ensures that no code enters the `bag/` or modifies `sam.py` unless it passes a static analysis and structural integrity check, reducing the need for manual rollbacks.

## Implementation Steps
1.  **Define `Critic` Class:** Create a new class in `sam.py` with a `validate(code: str)` method.
2.  **Integrate `ast` Validation:** Use `ast.parse()` to ensure the generated code is syntactically valid Python.
3.  **Integrate Linting:** Wrap `_dry_run_lint` inside the `Critic` to check for PEP8 compliance and undefined variables.
4.  **Inject into `apply_self_modification`:** Modify L612 to call `Critic.validate()` before proceeding to file I/O.
5.  **Feedback Loop:** If `Critic` fails, return the error trace to `_lint_fix_with_gemini` for an automated correction attempt before failing the cycle.

## Risk
**Failure Mode:** The `Critic` might be too aggressive, rejecting valid but complex architectural patterns (e.g., dynamic imports or metaprogramming).
**Mitigation:** Implement a "Force Override" flag for the `Critic` that requires a manual log entry, ensuring I don't get stuck in a loop if the `Critic` itself is flawed.

**Confidence Score:** 9/10