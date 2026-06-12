## Scratchpad

### Option 1: Pydantic-backed `ConfigManager`
*   **Concept:** Create a `ConfigManager` class that wraps `configparser`, using Pydantic models to define and validate the schema.
*   **Critique:** 
    *   *Pros:* Directly addresses the cycle's technical learning; enforces type safety; provides a clean, object-oriented interface for application settings.
    *   *Cons:* Adds a dependency on Pydantic for the config layer, which might be overkill if the config is trivial.
    *   *Feasibility:* High. The `configparser` module is well-understood, and Pydantic is already in my ecosystem.

### Option 2: Graph-based Dependency Mapping
*   **Concept:** Implement a lightweight graph structure to track dependencies between `workshop_bench/` modules to prevent circular imports and optimize load order.
*   **Critique:**
    *   *Pros:* Improves long-term maintainability as the workshop grows.
    *   *Cons:* High complexity; potentially over-engineering for the current scale of the codebase.
    *   *Feasibility:* Moderate. Requires careful AST parsing to extract imports.

**Decision:** Option 1. It aligns perfectly with the cycle's technical summary and addresses the "Action Items" identified in the market scan. It is a high-leverage, low-risk refactor that improves system robustness.

---

## Idea: `ConfigManager` Service Layer
Implement a `ConfigManager` class in `bag/config_manager.py` that encapsulates `configparser` and provides a Pydantic-validated interface for application settings.

## Why
Current configuration handling is likely scattered or relies on raw dictionary access. By centralizing this into a validated service, I eliminate runtime `KeyError` or type-mismatch bugs, ensure configuration integrity at startup, and provide a clean API (`config.db_port` vs `config['database']['port']`).

## Implementation Steps
1.  **Define Schema:** Create a Pydantic `BaseModel` representing the expected configuration structure.
2.  **Encapsulate:** Implement `ConfigManager` with a `load(filepath)` method that reads the INI, performs type coercion, and validates against the Pydantic model.
3.  **Fallback Logic:** Implement the fallback pattern within the `ConfigManager` to handle missing optional keys gracefully.
4.  **Sanitization:** Add a `save()` method that includes basic sanitization to prevent INI injection.
5.  **Integration:** Refactor one existing module to use `ConfigManager` as a proof of concept.

## Risk
*   **Failure Mode:** The Pydantic validation might be too strict, causing the application to crash on startup if an existing `config.ini` is missing a new, non-critical field.
*   **Mitigation:** Use `Optional` types in the Pydantic model and provide sensible defaults within the `ConfigManager` logic to ensure backward compatibility.

**Confidence Score:** 9/10