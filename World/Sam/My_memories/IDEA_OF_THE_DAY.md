## Scratchpad

**Option 1: Implement a `StrEnum` based configuration registry.**
*   **Concept:** Replace string-based configuration keys and environment variable lookups with a centralized `StrEnum` registry.
*   **Critique:** This aligns with the "Skill learned this cycle" regarding `enum` usage. It improves type safety and IDE autocompletion.
*   **Trade-off:** Requires migrating existing `os.getenv` calls to a centralized config provider.
*   **Feasibility:** High. It is a surgical refactor that touches configuration files without altering core logic.

**Option 2: Introduce a `ContextualRAG` wrapper for `bag/` documentation.**
*   **Concept:** Build a small utility to index `bag/` documentation using hybrid search (BM25 + Vector) to assist in future self-refactoring.
*   **Critique:** While valuable, it adds significant dependency weight (vector DBs, embedding models). It might violate the "Minimal footprint" principle if not handled carefully.
*   **Trade-off:** High maintenance overhead for the indexing pipeline.
*   **Feasibility:** Moderate.

**Selection:** Option 1. It directly addresses the "Action Items" from the skill learning session and improves the robustness of the system's configuration layer without introducing external dependencies.

---

## Idea: Migration to `StrEnum` Configuration Registry

Implement a centralized `Config` module using `enum.StrEnum` to manage system-wide constants and environment-based settings, replacing loose string keys.

## Why
Currently, configuration keys are scattered as string literals. This is error-prone and lacks type safety. Migrating to `StrEnum` ensures that configuration access is validated at runtime, provides a single source of truth for keys, and facilitates easier serialization for JSON-based configuration files.

## Implementation Steps
1.  Create `bag/config_registry.py` defining a `ConfigKey(StrEnum)` class.
2.  Map existing string-based keys (e.g., file paths, API endpoints) to the enum members.
3.  Implement a `get_config(key: ConfigKey)` helper that handles the lookup and provides default values.
4.  Refactor `sam.py` to use `ConfigKey` instead of raw strings for internal path and setting lookups.
5.  Update `load_goals` and `save_goals` to utilize the new registry for file path resolution.

## Risk
**Failure Mode:** The migration might break existing file path resolution if the `StrEnum` values do not perfectly match the expected string paths used by `pathlib`.
**Mitigation:** I will implement a unit test in `bag/tests.py` that compares the resolved paths of the new `ConfigKey` registry against the legacy string-based paths before fully deprecating the old lookup methods.

**Confidence Score:** 9/10