## Scratchpad

**Option 1: Implement `slots=True` across all high-frequency data structures.**
*   *Critique:* This directly addresses the self-correction note from the previous cycle. It is a low-risk, high-leverage refactor that improves memory efficiency and attribute access speed.
*   *Trade-offs:* Requires auditing all `dataclass` definitions. If a class uses multiple inheritance or requires dynamic attribute assignment, `slots` will break it.
*   *Feasibility:* High. Most of my data structures are simple state containers.

**Option 2: Introduce a `ValidationRegistry` for `__post_init__` logic.**
*   *Critique:* Currently, `__post_init__` logic is scattered. A centralized registry could allow for composable validation rules (e.g., `RangeValidator`, `TypeValidator`).
*   *Trade-offs:* Increases architectural complexity. Might be overkill for current needs.
*   *Feasibility:* Medium. Requires careful design to avoid creating a "God object" for validation.

**Decision:** Option 1 is more aligned with my current goal of "Minimal footprint, maximum leverage." It is a foundational improvement that prepares the codebase for larger agentic systems.

---

## Idea: Memory-Optimized Dataclass Migration
Refactor core state-holding dataclasses to use `slots=True` and `frozen=True` to enforce immutability and reduce memory overhead.

## Why
As I move toward more complex agentic workflows, the number of transient objects (e.g., `PatchOperation`, `Experience`, `Goal`) will increase. `slots=True` prevents the creation of `__dict__` for every instance, significantly reducing memory footprint and improving attribute access speed. `frozen=True` ensures that these objects remain predictable throughout the lifecycle of a cycle.

## Implementation Steps
1.  **Audit:** Identify all dataclasses in `sam.py` and `bag/` that are instantiated frequently.
2.  **Refactor:** Apply `slots=True` and `frozen=True` to these classes.
3.  **Validate:** Run `bag/tests.py` to ensure that no code relies on dynamic attribute assignment or mutation of these objects.
4.  **Cleanup:** Ensure all mutable defaults are handled via `field(default_factory=...)` as per the previous cycle's learning.

## Risk
**Failure Mode:** A legacy component might be attempting to monkey-patch or dynamically add attributes to a dataclass instance at runtime.
**Mitigation:** The `self_check()` (Ruff) and `behaviour_check()` (tests.py) will catch attribute errors immediately. I will perform the refactor in small, incremental patches to isolate any regressions.

**Confidence Score: 9/10**