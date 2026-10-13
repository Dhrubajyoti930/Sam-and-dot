## Scratchpad

**Option 1: Capability-Based File System Proxy**
*   **Concept:** Replace direct `Path` operations in `sam.py` with a `CapabilityProxy` that requires a `Token` object.
*   **Critique:** High impact on security (removes ambient authority). However, it requires refactoring almost every file-system-touching function in `sam.py` and `bag/`.
*   **Trade-off:** High maintenance burden vs. significant security gain.
*   **Feasibility:** Moderate; requires careful surgical patching to avoid breaking the `rollback_registry` or `workshop_bench` logic.

**Option 2: Revocable Capability Forwarder (The "Lease" Pattern)**
*   **Concept:** Implement a `Lease` object for external API calls. When an agent requests an API call, it receives a `Lease` that expires after a set number of tokens or time.
*   **Critique:** Addresses the "Revocation" weakness identified in my self-correction. It is less invasive than a full FS rewrite.
*   **Trade-off:** Adds complexity to the `ask_gemini` flow.
*   **Feasibility:** High; can be implemented as a wrapper around `CLIENT.models.generate_content`.

**Decision:** I will pursue **Option 2**. It directly addresses the "Revocation" weakness and aligns with the "Minimal footprint, maximum leverage" core trait.

---

## Idea: Revocable Lease Pattern for Gemini API Calls

Implement a `Lease` context manager for `ask_gemini` that enforces token-budgeting and automatic revocation of the "capability" to call the LLM once a task-specific limit is reached.

## Why
Currently, `ask_gemini` is a global utility. If an agent is compromised, it has ambient authority to call the LLM indefinitely. By wrapping calls in a `Lease`, I enforce the Principle of Least Privilege (PoLP) and ensure that even if an agent is hijacked, its ability to consume resources or generate output is strictly bounded by the `Lease` scope.

## Implementation Steps
1.  **Define `Lease` class:** Create `bag/security.py` with a `Lease` class that tracks `max_tokens` and `is_active`.
2.  **Update `ask_gemini`:** Modify `ask_gemini` to accept an optional `lease` argument.
3.  **Enforce Revocation:** If `lease.is_active` is false, `ask_gemini` raises a `SecurityViolation` exception.
4.  **Integration:** Update `phase_i_deep_learning` and `phase_v_development` to instantiate a `Lease` before calling `ask_gemini`.

## Risk
*   **Failure Mode:** The `Lease` object might be incorrectly passed or ignored by future sub-tasks, leading to "zombie" calls.
*   **Mitigation:** Implement a `get_current_lease()` thread-local storage mechanism so that `ask_gemini` defaults to a "Zero-Capability" state if no lease is active in the current execution context.

**Confidence Score: 8/10** (The pattern is well-understood; the primary risk is the complexity of thread-local state management in an asynchronous-adjacent environment).