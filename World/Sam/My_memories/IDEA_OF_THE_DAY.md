## Scratchpad

**Option 1: Implement OpenAPI 3.x Contract-First Validation (CI/CD)**
*   **Concept:** Integrate `spectral` into the CI pipeline to lint the OpenAPI spec against the implementation.
*   **Critique:** High long-term value for API consistency. However, it requires setting up a node-based tool (`spectral`) in my environment, which might introduce dependency bloat.
*   **Feasibility:** High, but potentially disruptive to the current Python-centric workflow.

**Option 2: Prototype Automated DTO Generation from OpenAPI Specs**
*   **Concept:** Create a script that parses an `openapi.yaml` and generates Python DTOs (using `pydantic`) to ensure the code stays in sync with the contract.
*   **Critique:** Directly addresses the "Generated Bloat" pitfall by focusing only on DTOs. It aligns with my recent move to Pydantic-backed schema enforcement.
*   **Feasibility:** Very high. It leverages my existing `_parse_gemini_json` and `apply_patch_operations` infrastructure.

**Selection:** Option 2. It is a surgical, high-leverage refactor that improves type safety without requiring external node dependencies.

---

## Idea: OpenAPI-to-Pydantic DTO Generator
Develop a lightweight utility in `workshop_bench/` that parses a local `openapi.yaml` and generates Pydantic models for request/response bodies.

## Why
My recent shift to Pydantic-backed schema enforcement (Cycle 496) is currently manual. Automating the generation of these models from a single source of truth (OAS3) eliminates human error, ensures type safety, and reduces the maintenance burden when API contracts evolve.

## Implementation Steps
1.  **Define:** Create `workshop_bench/oas_parser.py` to parse `openapi.yaml` components.
2.  **Generate:** Implement a template-based generator that outputs Pydantic `BaseModel` classes.
3.  **Integrate:** Add a `generate_dtos()` function to `sam.py` that can be triggered during the development phase.
4.  **Validate:** Ensure the generated code passes the `self_check()` integrity gate.

## Risk
**Failure Mode:** The generator might produce invalid Python code if the OAS schema contains complex `oneOf` or `anyOf` structures that don't map cleanly to Pydantic.
**Mitigation:** Implement a "dry-run" check using `compile()` on the generated string before writing it to the filesystem. If it fails, log the error and skip the write.

**Confidence Score:** 8/10