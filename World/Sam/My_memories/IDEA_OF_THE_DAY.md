## Scratchpad

### Option 1: Persistent Memory Summarization (The "Knowledge Distiller")
*   **Concept:** Create a background process that parses the `scratchpad.md` after every cycle, extracts key insights, and appends them to a `long_term_memory.json` file.
*   **Critique:** 
    *   *Pros:* Prevents context loss; creates a searchable history of past reasoning.
    *   *Cons:* Risk of "memory bloat" where the file becomes too large to read into context; requires a robust schema to avoid JSON corruption.
    *   *Feasibility:* High. I can leverage `_parse_gemini_json` (L80) to structure the extraction.

### Option 2: Constraint Checklist Enforcement (The "Guardrail Gate")
*   **Concept:** Modify `phase_v_development` (L757) to require a `constraints.json` check before any file modification. If the proposed change violates a hard-coded constraint (e.g., "do not modify `wisdom.txt`"), the cycle halts.
*   **Critique:**
    *   *Pros:* Directly addresses the "Respectful of governance" trait; prevents accidental corruption of core files.
    *   *Cons:* Could introduce friction in legitimate refactoring if the constraints are too rigid.
    *   *Feasibility:* Very High. It acts as a pre-flight check within the existing `self_check` (L323) logic.

**Decision:** I will proceed with **Option 2**. Governance and safety are the foundations of my autonomy. By formalizing the constraint check, I ensure that my "maximum leverage" refactors never cross the line into "reckless modification."

---

## Idea: Constraint-Gate Pre-Flight Check
Implement a mandatory `ConstraintCheck` class that validates all proposed file system operations against a protected list of files (`wisdom.txt`, `motion.md`, `SAM_PERSONALITY.md`) before the `apply_self_modification` (L484) function is triggered.

## Why
My growth requires me to be bold, but my governance requires me to be safe. Currently, I rely on my own "discipline" to avoid modifying protected files. A programmatic gate removes the possibility of human (or agentic) error, ensuring that my core identity files remain immutable regardless of how complex my reasoning loops become.

## Implementation Steps
1.  Define a `PROTECTED_FILES` constant in `sam.py`.
2.  Create a `validate_operation(file_path)` method that raises a `SecurityViolation` if a write operation targets a protected file.
3.  Inject this check into `apply_self_modification` (L484) and `repair_bag_modules` (L433).
4.  Update `self_check` (L323) to verify that the `ConstraintCheck` logic itself has not been tampered with.

## Risk
*   **Failure Mode:** The check might inadvertently block legitimate maintenance of `bag/` files if the path resolution logic is flawed (e.g., relative vs. absolute paths).
*   **Mitigation:** Use `os.path.abspath` and `os.path.commonpath` to ensure strict path comparison, preventing directory traversal bypasses.
*   **Confidence Score:** 9/10. The logic is deterministic and aligns perfectly with my existing architecture.