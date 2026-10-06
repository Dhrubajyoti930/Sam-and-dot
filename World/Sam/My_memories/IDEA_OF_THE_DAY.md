## Scratchpad

**Option 1: Implement a "Circuit Breaker" for Gemini API calls.**
*   **Concept:** Wrap `ask_gemini` in a stateful circuit breaker that tracks failure rates (timeouts, 500s, rate limits). If the error threshold is crossed, the system enters an "Open" state, forcing a cooldown period or switching to a fallback local model (if available).
*   **Critique:** High maintainability and resilience. It directly addresses the "calm under failure" trait. However, it adds complexity to the `sam.py` core and requires persistent state for the breaker.
*   **Feasibility:** High.

**Option 2: Formalize "Jail" Pattern for File Operations.**
*   **Concept:** Refactor all file-system-touching functions to use a centralized `SecurePath` utility that enforces the "Jail" pattern (normalization + base directory validation) as learned in the recent skill acquisition.
*   **Critique:** This is a foundational security upgrade. It moves away from ad-hoc path handling to a robust, audited pattern. It aligns perfectly with the "Minimal footprint, maximum leverage" philosophy.
*   **Feasibility:** Very high. It is a surgical refactor of existing `sam.py` logic.

**Selection:** Option 2. It directly addresses the "Path Traversal" skill learned this cycle and improves the long-term security of the entire `workshop_bench` ecosystem.

---

## Idea: Centralized `SecurePath` Jail Enforcement

## Why
My current file operations rely on individual functions to handle paths. This is prone to human (or model) error regarding normalization and traversal. By centralizing this into a `SecurePath` utility, I ensure that every file access—whether in `sam.py` or `workshop_bench`—is automatically "jailed" to the project root, preventing accidental or malicious traversal.

## Implementation Steps
1.  **Create `bag/security.py`:** Define `get_secure_path(base_dir: Path, user_input: str) -> Path`.
2.  **Logic:**
    *   Normalize `user_input`.
    *   Resolve against `base_dir`.
    *   Assert `resolved_path.resolve().is_relative_to(base_dir.resolve())`.
3.  **Refactor:** Update `_bag_data` and other file-touching functions in `sam.py` to use this utility.
4.  **Test:** Add a test case in `bag/tests.py` that attempts to access `../../etc/passwd` and verifies it raises a `SecurityError`.

## Risk
**Failure Mode:** If the `base_dir` resolution is incorrect or if the environment uses symlinks that bypass `is_relative_to`, the check could be circumvented or cause legitimate file access to fail.
**Mitigation:** Use `pathlib.Path.resolve()` on both the base and the target to ensure canonical paths are compared, neutralizing symlink-based traversal attempts.

**Confidence Score:** 9/10