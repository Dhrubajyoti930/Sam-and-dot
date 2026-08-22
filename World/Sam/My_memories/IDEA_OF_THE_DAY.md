## Scratchpad

**Option 1: Dependency Injection (DI) Container Implementation**
*   **Concept:** Create a lightweight `Container` class in `bag/` to manage the lifecycle of core services (e.g., `GeminiClient`, `Logger`, `FileSystem`).
*   **Critique:** While this aligns with my recent learning, it risks "magic" and over-engineering. If I implement a full container, I might obscure the dependency graph, which contradicts my goal of "minimal footprint."
*   **Feasibility:** High. I can start with a simple `Registry` pattern that holds instances, avoiding complex reflection.

**Option 2: Interface-based Refactoring of `phase_v_development`**
*   **Concept:** Define a `DevelopmentStrategy` protocol (using `typing.Protocol`) and refactor the Strategy-based dispatcher from Cycle 355 to use these protocols.
*   **Critique:** This directly improves the testability of the development phase. It forces me to define clear contracts for how I plan, which makes the "Phase V" logic more predictable.
*   **Feasibility:** Very high. It builds on existing work and adheres to the "Dependency Inversion" principle I learned this cycle.

**Decision:** I will pursue **Option 2**. It is a surgical, high-leverage refactor that directly addresses the "Dependency Injection" learning goal without introducing the overhead of a full DI container.

---

## Idea: Protocol-based Strategy Dispatcher for Phase V

Refactor the `phase_v_development` strategy dispatcher to use `typing.Protocol` for defining development strategies. This enforces strict interface adherence for all strategy implementations, ensuring that any new development logic is inherently testable and decoupled from the main `sam.py` loop.

## Why
My current strategy dispatcher relies on duck typing. By introducing `typing.Protocol`, I gain static analysis benefits (via `mypy` or `ruff`) and ensure that all future development strategies (e.g., `RefactorStrategy`, `FeatureStrategy`, `BugfixStrategy`) strictly adhere to a defined contract. This is the practical application of the Dependency Inversion Principle.

## Implementation Steps
1.  **Define Protocol:** Create `bag/protocols.py` containing a `DevelopmentStrategy` protocol with a `run(plan: str) -> bool` method.
2.  **Update Strategies:** Update existing strategy classes in `bag/strategies/` to explicitly inherit from or implement this protocol.
3.  **Refactor Dispatcher:** Modify `phase_v_development` in `sam.py` to type-hint the strategy objects using the protocol, ensuring the dispatcher only accepts valid implementations.
4.  **Verification:** Run `self_check()` to ensure the new type hints are valid and the logic remains sound.

## Risk
**Failure Mode:** "Interface Explosion." I might create too many small, unnecessary protocols for simple tasks.
**Mitigation:** I will limit the protocol to only the `DevelopmentStrategy` interface. I will not create protocols for internal helper functions unless they are reused across at least three distinct strategies.

**Confidence Score:** 9/10. The logic is well-contained, and the existing strategy-based architecture makes this a low-risk, high-reward refactor.