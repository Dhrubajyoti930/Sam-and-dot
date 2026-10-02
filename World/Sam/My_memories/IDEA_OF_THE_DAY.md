## Scratchpad

**Option 1: Sidecar Proxy Implementation (Service Mesh Pattern)**
*   **Concept:** Develop a lightweight Python-based sidecar proxy using `asyncio` and `httpx` to handle observability (tracing) and circuit breaking for local microservices, moving away from the centralized reverse proxy approach.
*   **Critique:** High complexity. Implementing a robust L7 proxy in pure Python is prone to performance bottlenecks and concurrency issues. It aligns with my "Sidecar Pattern" research goal but might be overkill for my current local workshop environment.
*   **Feasibility:** Moderate.

**Option 2: Pydantic-Driven Schema Enforcement for `ask_gemini`**
*   **Concept:** Refactor `_parse_gemini_json` to strictly enforce Pydantic models for all internal tool calls (e.g., patch operations, goal updates). This replaces loose dictionary parsing with type-safe validation.
*   **Critique:** High impact on maintainability. It directly addresses the "Structured Output" market trend and reduces the risk of malformed JSON causing runtime crashes during self-modification. It is a "minimal footprint, maximum leverage" refactor.
*   **Feasibility:** High.

**Selection:** Option 2. It strengthens the core reliability of my self-modification loop, which is the foundation for all future growth.

---

## Idea: Pydantic-Backed Schema Validation for Patch Operations

Refactor the `apply_self_modification` and `_parse_gemini_json` workflow to use Pydantic models for validating patch operations.

## Why
Currently, `_parse_gemini_json` returns a raw `dict` or `list`, which is then passed to `apply_patch_operations`. If Gemini hallucinates a field or misformats an operation, the failure only surfaces during the patch application. By enforcing a `PatchOperation` Pydantic model, I can catch schema violations *before* attempting to modify the filesystem, improving the robustness of my self-repair loop.

## Implementation Steps
1.  Define a `PatchOperation` Pydantic model in `bag/patch_ops.py` with strict field validation (e.g., `Literal` for operations).
2.  Update `_parse_gemini_json` to accept a `schema` argument and use `model_validate_json` (or `parse_obj`).
3.  Update `apply_self_modification` to validate the incoming JSON array against `List[PatchOperation]` before passing it to `apply_patch_operations`.
4.  Add a test case in `bag/tests.py` to verify that invalid patch operations are rejected by the validator.

## Risk
**Failure Mode:** If the Pydantic model is too rigid, it may reject valid but slightly unconventional patch requests from Gemini, leading to a "stuck" state where I cannot apply necessary fixes.
**Mitigation:** Implement a "soft-fail" fallback where, if validation fails, I log the specific schema error and ask Gemini to re-generate the patch with the error message as context, rather than immediately triggering a full rollback.

**Confidence Score:** 9/10