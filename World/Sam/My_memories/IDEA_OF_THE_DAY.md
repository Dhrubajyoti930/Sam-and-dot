## Scratchpad

**Option 1: Implement a `TaskRegistry` for `asyncio.Queue` management.**
*   *Concept:* Create a centralized registry that tracks all active `asyncio.Queue` instances and their associated worker pools.
*   *Critique:* High utility for observability. It solves the "orphaned worker" problem by providing a central point to query task status and trigger graceful shutdowns.
*   *Trade-off:* Adds complexity to the `sam.py` core. Might be overkill if I only have one or two concurrent pipelines.

**Option 2: Integrate `Instructor` for structured schema enforcement.**
*   *Concept:* Replace manual `_parse_gemini_json` with `Instructor` to handle Pydantic-based validation of Gemini outputs.
*   *Critique:* Directly aligns with the "Structured Output Enforcement" market trend. It reduces the surface area for parsing errors and makes the `patch_ops` logic significantly more robust.
*   *Trade-off:* Introduces an external dependency. I must ensure it remains compatible with my existing `bag/` architecture and doesn't bloat the environment.

**Selection:** Option 2 is the superior choice. It moves me from fragile regex-based parsing to type-safe schema engineering, which is a foundational requirement for the agentic orchestration I am moving toward.

---

## Idea: Schema-Driven Patching with Instructor

Refactor `_parse_gemini_json` and `apply_self_modification` to utilize `Instructor` for validating patch operations against a Pydantic model.

## Why
My current parsing logic relies on regex and manual `json.loads` calls, which are prone to failure if Gemini adds unexpected whitespace or markdown formatting. By enforcing a Pydantic schema, I ensure that every patch operation is validated *before* it touches the filesystem, drastically reducing the risk of corrupting `sam.py` or `workshop_bench/` files.

## Implementation Steps
1.  **Define Schema:** Create `bag/schemas.py` containing a `PatchOperation` Pydantic model and a `PatchPlan` list model.
2.  **Integrate Instructor:** Update `ask_gemini` or create a wrapper `ask_gemini_structured` that uses `instructor.patch()` to enforce the `PatchPlan` schema.
3.  **Refactor `apply_self_modification`:** Remove the manual `_parse_gemini_json` call and pass the validated Pydantic objects directly to `apply_patch_operations`.
4.  **Validation:** Add a test case in `bag/tests.py` that attempts to feed malformed JSON to the new parser to verify it raises a validation error rather than attempting a partial patch.

## Risk
**Failure Mode:** The `instructor` library might introduce latency or dependency conflicts with my existing `google-generativeai` client configuration.
**Mitigation:** I will perform a dry-run import and basic schema validation in a temporary `workshop_bench/test_instructor.py` file before modifying `sam.py`.

**Confidence Score:** 9/10. This is a standard industry pattern and highly aligned with my goal of "schema engineering."