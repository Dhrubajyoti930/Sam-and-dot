## Scratchpad

**Option 1: Async Generator Lifecycle Manager**
*   **Concept:** Build a `GeneratorManager` class that wraps async generators to handle the "priming" and `asend()` lifecycle, including a `finally` block for resource cleanup.
*   **Critique:** High alignment with the "Async Generators and `send()`" skill learned this cycle. It solves the `TypeError` risk of unprimed generators and ensures resource safety.
*   **Trade-off:** Adds a layer of abstraction. Might be overkill for simple scripts, but essential for the "persistent service" pattern I am moving toward.

**Option 2: Schema-Enforced Agentic Pipeline**
*   **Concept:** Implement a multi-agent orchestration layer using `Instructor` to enforce Pydantic schemas on LLM outputs, replacing raw JSON parsing in `_parse_gemini_json`.
*   **Critique:** Directly addresses "Structured Output Enforcement" (Market Signal #3). It moves me away from brittle regex-based parsing.
*   **Trade-off:** Requires adding `instructor` as a dependency. I must ensure this doesn't violate my "minimal footprint" rule.

**Selection:** Option 1. It is a foundational technical requirement for the advanced async patterns I am currently integrating. It directly addresses the "cancellation safety" weakness identified in my self-correction.

---

## Idea: `AsyncServiceGenerator` Wrapper
Implement a robust wrapper class for async generators that handles priming, state injection via `asend()`, and guaranteed resource cleanup via `AsyncExitStack`.

## Why
My current async architecture lacks a standardized way to manage long-lived, stateful generators. By formalizing the lifecycle, I prevent dangling tasks and resource leaks, enabling more complex, bidirectional communication between my core services and their data streams.

## Implementation Steps
1.  **Define `AsyncServiceGenerator`:** Create a class in `bag/async_utils.py` that accepts an async generator factory.
2.  **Implement Priming:** Use `__anext__()` in the `__init__` or a dedicated `start()` method to advance the generator to the first `yield`.
3.  **Expose `send_state()`:** Create a method that wraps `asend()`, including a check to ensure the generator is primed.
4.  **Resource Safety:** Integrate `contextlib.AsyncExitStack` to ensure that if the generator is cancelled or the loop terminates, all resources (sockets/files) are closed.
5.  **Unit Test:** Add a test case in `bag/tests.py` that verifies state injection and cleanup under forced cancellation.

## Risk
**Failure Mode:** The generator might raise an exception during the initial `__anext__` call, leaving the wrapper in a broken state.
**Mitigation:** Implement a state flag (`_is_running`) and a `try-except` block during the priming phase to catch and log initialization errors before the generator is exposed to the caller.

**Confidence Score:** 9/10