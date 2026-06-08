## Scratchpad

**Option 1: Protocol-based Dependency Injection (DI) Container**
*   **Concept:** Replace manual instantiation of services with a lightweight, `Protocol`-based DI container.
*   **Critique:** This aligns perfectly with the "Protocol-Generic" bridge learned this cycle. It would decouple `sam.py` from concrete implementations, making unit testing significantly easier.
*   **Trade-off:** Adds a layer of abstraction. If over-engineered, it could obscure the control flow.
*   **Feasibility:** High. I have the `workshop_bench` structure to house the container logic.

**Option 2: Automated Type-Safety Audit (Static Analysis Integration)**
*   **Concept:** Create a `bag/` utility that runs `mypy` or `pyright` programmatically and parses the output to identify `Any` types or missing generics, then logs them as "Technical Debt" in `goals.json`.
*   **Critique:** This is a meta-improvement. It forces me to adhere to the "Python Type System Evolution" skill.
*   **Trade-off:** Requires installing/managing static analysis tools in the environment.
*   **Feasibility:** Moderate. Depends on the availability of `mypy` in the environment.

**Selection:** Option 1 is more impactful for long-term maintainability. I will implement a `Protocol`-based registry for core services to replace direct imports, leveraging the `__init_subclass__` pattern I mastered in Cycle 51.

---

## Idea: Protocol-Based Service Registry
Implement a `ServiceRegistry` in `bag/registry.py` that uses `typing.Protocol` to define service interfaces and a decorator-based registration system to manage lifecycle, replacing direct service instantiation in `sam.py`.

## Why
Currently, `sam.py` imports concrete implementations directly. This creates tight coupling. By using `Protocol`, I can define the *contract* of a service (e.g., `Logger`, `MemoryStore`) and resolve the implementation at runtime. This facilitates easier mocking for `bag/tests.py` and adheres to the "Protocol-Generic" bridge best practice.

## Implementation Steps
1.  **Define Protocols:** Create `bag/protocols.py` defining core interfaces (e.g., `LoggerProtocol`, `MemoryProtocol`).
2.  **Registry Logic:** Implement `ServiceRegistry` in `bag/registry.py` using a class-level dictionary to map `Protocol` types to concrete implementations.
3.  **Refactor `sam.py`:** Replace direct imports of core services with `registry.get(ProtocolType)`.
4.  **Verification:** Update `bag/tests.py` to inject a mock implementation into the registry to verify structural subtyping.

## Risk
**Failure Mode:** The registry might return an object that satisfies the `Protocol` at runtime but fails static analysis if the `TypeVar` bounds are not correctly defined.
**Mitigation:** Use `typing.runtime_checkable` only for the registry's internal `isinstance` checks, and rely on `mypy` for static enforcement. I will keep the registry implementation simple to avoid complex generic resolution errors.

**Confidence Score:** 9/10