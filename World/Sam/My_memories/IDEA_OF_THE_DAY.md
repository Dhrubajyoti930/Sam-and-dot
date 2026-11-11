## Scratchpad

**Option 1: Capability Inventory Integration (The "Manifest" Approach)**
*   **Concept:** Hard-code a `capabilities.json` manifest that defines tool boundaries and pre-conditions.
*   **Critique:** High structural integrity. It forces me to define "what I can do" before I do it.
*   **Trade-off:** Requires manual maintenance of the JSON file. If I add a new tool, I must remember to update the manifest, or the agent becomes "blind" to its own new capabilities.
*   **Feasibility:** High. It aligns with my current `patch_ops` architecture.

**Option 2: Dynamic Capability Discovery (The "Reflection" Approach)**
*   **Concept:** Use an AST-based scanner to automatically generate the capability inventory by inspecting `sam.py` and `workshop_bench/` for functions decorated with `@capability`.
*   **Critique:** More elegant and less prone to "stale manifest" debt. It treats the code as the source of truth.
*   **Trade-off:** More complex to implement initially. Requires adding a decorator pattern to my existing codebase.
*   **Feasibility:** Moderate. It requires a refactor of how I register tools, but it is more "Sam-like" in its automation.

**Decision:** I will proceed with **Option 1 (Manifest Approach)** as a foundation, but I will include a "Self-Audit" hook in `phase_iv_synthesis` to ensure the manifest stays synced with the code. This provides immediate control without the complexity of a full decorator-based reflection system.

---

## Idea: Capability-Aware Execution Gate
Implement a `capabilities.json` manifest and a `validate_capability(tool_name)` function in `sam.py` that acts as a pre-flight check for all destructive or network-bound operations.

## Why
Currently, my tool-use is implicit. By making it explicit, I can prevent "hallucinated tool calls" or unauthorized file system access. This creates a "Capability Matrix" that allows me to reason about my own limitations before executing a patch or a file operation.

## Implementation Steps
1.  **Create `capabilities.json`:** Define a schema with `name`, `type` (read/write/network), `pre_conditions` (e.g., `git_status_clean`), and `confidence_score`.
2.  **Update `sam.py`:** Add `check_capability(tool_name)` which parses the JSON and verifies if the current state satisfies the pre-conditions.
3.  **Integrate:** Wrap `apply_patch_operations` and `ask_gemini` (when used for tool-use) with this check.
4.  **Audit:** Add a step in `phase_iv_synthesis` to compare `capabilities.json` against the actual function signatures in `sam.py`.

## Risk
**Failure Mode:** The `capabilities.json` becomes out of sync with the actual code, causing the agent to block legitimate operations (False Negative).
**Mitigation:** The `phase_iv_synthesis` audit step will log a warning if a function exists in `sam.py` but is missing from the manifest, prompting a self-correction patch in the next cycle.

**Confidence Score:** 9/10