## Scratchpad

**Option 1: Service Mesh "Ambient" Prototype**
*   **Concept:** Implement a local-first, sidecar-less traffic management layer using `httpx` middleware to simulate Envoy's circuit-breaking and retry logic.
*   **Critique:** High complexity. While it aligns with the "Service Mesh" skill, building a custom proxy layer in Python is prone to performance bottlenecks and "reinventing the wheel." It risks adding significant technical debt to `sam.py` for a feature that might be better served by existing libraries like `tenacity`.
*   **Feasibility:** Moderate.

**Option 2: Pydantic-Driven Agentic State Machine**
*   **Concept:** Refactor the `run_cycle` state management to use a Pydantic-based state machine. Instead of loose dictionary passing, define a `CycleState` model that enforces transitions between phases (I-VII).
*   **Critique:** High alignment with "Structured Output & Pydantic-Driven AI." It improves maintainability by making the `run_cycle` flow deterministic and type-safe. It directly addresses the "long-term maintainability" requirement of my character.
*   **Feasibility:** High. It leverages existing `_parse_gemini_json` infrastructure.

**Decision:** Option 2. It is a surgical refactor that improves the core engine's reliability without the overhead of a full service mesh.

---

## Idea: Pydantic-Driven Cycle State Machine

Refactor the `run_cycle` function to utilize a `CycleState` Pydantic model to manage data flow between phases, replacing the current loose dictionary passing.

## Why
Currently, `run_cycle` passes a `goals` dictionary that is prone to key-error bugs and lacks schema enforcement. By defining a `CycleState` model, I can ensure that each phase receives exactly the data it needs, and that the output of each phase is validated before the next begins. This reduces the risk of state corruption during self-modification.

## Implementation Steps
1.  Define `CycleState(BaseModel)` in `sam.py` with fields for `goals`, `market_data`, `skill`, `idea`, `plan`, and `evolution`.
2.  Update `run_cycle` to instantiate `CycleState` at the start of the loop.
3.  Modify phase functions (`phase_i_deep_learning`, etc.) to accept and return the `CycleState` object or specific validated fields.
4.  Add a validation step at the end of each phase to ensure the `CycleState` remains consistent.

## Risk
**Failure Mode:** The transition to a strict schema might break existing helper functions that expect a raw dictionary, leading to runtime `AttributeError` or `ValidationError`.
**Mitigation:** Implement a temporary `to_dict()` method on the `CycleState` model to maintain backward compatibility with legacy helpers while I migrate them one by one.

**Confidence Score:** 9/10