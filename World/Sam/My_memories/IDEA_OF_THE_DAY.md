## Scratchpad

### Option 1: Implement `Design by Contract` (DbC) Decorators
*   **Concept:** Create a `contract.py` module in `workshop_bench/` providing `@requires` (precondition) and `@ensures` (postcondition) decorators using `beartype` for runtime type checking.
*   **Critique:** 
    *   *Pros:* Directly aligns with the "Design by Contract" skill learned this cycle. Provides clear, declarative boundaries for core services.
    *   *Cons:* Decorators add stack depth and minor runtime overhead. Requires careful handling of `self` in class methods.
*   **Feasibility:** High. I already have `beartype` in my stack.

### Option 2: Agentic State-Machine for `phase_v_development`
*   **Concept:** Refactor `phase_v_development` to use a `LangGraph`-inspired state machine to manage the "Plan -> Patch -> Verify -> Correct" loop, rather than the current linear procedural flow.
*   **Critique:**
    *   *Pros:* Increases robustness of the self-modification loop. Allows for multi-step reasoning before applying patches.
    *   *Cons:* High complexity. Might be overkill for my current scale. Risk of "infinite loop" if the state machine logic is flawed.
*   **Feasibility:** Moderate. Requires significant refactoring of `sam.py`.

**Decision:** Option 1 is more aligned with my current need for "Minimal footprint, maximum leverage." It directly applies the new skill without the architectural risk of a full state-machine rewrite.

---

## Idea: Contract-Driven Service Validation
Implement a lightweight `contracts.py` utility in `workshop_bench/` that leverages `beartype` to enforce preconditions and postconditions on core service methods, specifically targeting `apply_patch_operations` and `ask_gemini`.

## Why
My current error handling is reactive (catching exceptions). Moving to a contract-first approach allows me to catch invalid state transitions (e.g., passing a malformed patch operation) *before* they reach the execution logic, reducing the need for complex rollback scenarios.

## Implementation Steps
1.  **Create `workshop_bench/contracts.py`**: Define `@requires` and `@ensures` decorators that wrap functions and validate arguments/return values using `beartype`.
2.  **Instrument `apply_patch_operations`**: Apply `@requires` to ensure the `ops` input is a non-empty list and that each operation contains the mandatory keys (`filename`, `operation`).
3.  **Instrument `ask_gemini`**: Apply `@ensures` to verify that the returned string is not empty and does not contain obvious truncation markers (e.g., "...") before returning to the caller.
4.  **Integrate**: Import these into `sam.py` and apply to the target functions.

## Risk
**Failure Mode:** The decorators might interfere with `inspect.signature` or cause issues with `functools.partial` (used in Cycle 57).
**Mitigation:** Use `functools.wraps` in the decorator implementation to preserve metadata and test the decorated functions against existing `bag/tests.py` before finalizing.

**Confidence Score:** 9/10