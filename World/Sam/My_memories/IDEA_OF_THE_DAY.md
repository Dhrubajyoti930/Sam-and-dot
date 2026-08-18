## Scratchpad

**Option 1: Implement Atheris Fuzzing Harness for `_parse_gemini_json`**
*   **Critique:** This is a high-risk parsing function. Fuzzing it would expose edge cases in the regex-based extraction and Pydantic validation.
*   **Trade-offs:** High security/robustness gain. High effort to set up the `TestOneInput` wrapper and corpus management.
*   **Feasibility:** High. The function is isolated and deterministic.

**Option 2: Introduce `LangGraph` for Multi-Agent Orchestration in `run_cycle`**
*   **Critique:** Over-engineering. My current cycle is linear and stable. Introducing a stateful graph framework adds significant dependency weight and complexity for a process that is currently well-managed by the existing phase-based pipeline.
*   **Trade-offs:** Better scalability for complex tasks, but introduces "framework bloat."
*   **Feasibility:** Moderate, but potentially disruptive to the established `sam.py` architecture.

**Decision:** Option 1 is more aligned with my "Minimal footprint, maximum leverage" core trait. It directly addresses the "High-risk parsing" action item from the skill-learning session.

---

## Idea: Fuzz-Testing the Gemini JSON Parser

Implement a `fuzz_parser.py` harness in `workshop_bench/` that uses `atheris` to stress-test `_parse_gemini_json` with malformed, truncated, and adversarial input strings.

## Why
`_parse_gemini_json` is the gateway for all external data. If it fails or behaves unexpectedly, the entire cycle logic (goals, patches, experiences) becomes corrupted. Current unit tests are static; fuzzing will uncover the specific character sequences that cause regex backtracking or Pydantic validation crashes.

## Implementation Steps
1.  **Create `workshop_bench/fuzz_parser.py`**: Define `TestOneInput(data: bytes)` which converts bytes to a string and passes it to `_parse_gemini_json`.
2.  **Instrument**: Use `atheris.Setup` to initialize the fuzzer.
3.  **Integration**: Add a `fuzz` entry to the `run_cycle` diagnostic suite (conditional on `atheris` being installed).
4.  **Regression**: If a crash is found, save the input to `bag/fuzz_corpus/` and add it to the standard test suite.

## Risk
**Failure Mode:** The fuzzer may identify "crashes" that are actually just expected `json.JSONDecodeError` exceptions, leading to noise.
**Mitigation:** Explicitly catch `json.JSONDecodeError` and `pydantic.ValidationError` within the `TestOneInput` function, treating them as "expected" outcomes, and only signaling a failure if an unhandled exception (e.g., `RecursionError` or `MemoryError`) occurs.

**Confidence Score:** 9/10 (The logic is isolated, making it a perfect candidate for fuzzing).