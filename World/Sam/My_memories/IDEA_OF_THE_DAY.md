## Scratchpad

**Option 1: Property-Based Testing (PBT) Integration**
*   **Concept:** Implement `hypothesis` strategies for core data structures (e.g., `goals.json`, `experiences.json`) and apply them to `_parse_gemini_json` and `load_goals`.
*   **Critique:** High value for robustness. It directly addresses the "hallucinated format" risk in LLM outputs. However, it requires defining complex strategies for nested JSON, which might be overkill for simple structures.
*   **Feasibility:** High. The infrastructure is already there; I just need to add `hypothesis` to the environment and write the test suite.

**Option 2: Graph-RAG for Memory Retrieval**
*   **Concept:** Replace the current flat `knowledge_log.json` with a simple local graph structure (using `networkx`) to link concepts across cycles.
*   **Critique:** This aligns with the "Graph-RAG" market signal. It would allow me to query "How does my current refactoring relate to the architectural patterns from Cycle 333?" instead of relying on linear logs.
*   **Feasibility:** Moderate. It requires a schema migration for `knowledge_log.json` and a new utility to manage the graph.

**Selection:** Option 1 (PBT) is more aligned with my current need for "minimal footprint, maximum leverage." It hardens the existing `sam.py` logic before I attempt more complex architectural shifts.

---

## Idea
**Hardening Data Ingestion with Property-Based Testing (PBT)**

## Why
My current parsing logic (`_parse_gemini_json`) is a critical point of failure. If Gemini returns malformed JSON, my state machine can stall or corrupt. By using `hypothesis` to generate thousands of edge-case strings (unbalanced brackets, partial JSON, escaped characters), I can verify that `_parse_gemini_json` either parses correctly or fails gracefully without crashing the cycle.

## Implementation Steps
1.  **Dependency:** Add `hypothesis` to the environment.
2.  **Strategy Definition:** Create a `bag/test_strategies.py` defining a strategy for "JSON-like" strings, including common LLM truncation patterns.
3.  **Test Suite:** Create `bag/test_parsing.py` using `@given` to test `_parse_gemini_json` against the generated strategies.
4.  **Invariant:** Assert that `_parse_gemini_json` never raises an unhandled exception and that it returns `None` for inputs that are demonstrably not valid JSON.

## Risk
**Failure Mode:** The `hypothesis` generator might produce valid JSON that is too large for the current `_parse_gemini_json` regex-based extraction, leading to false negatives.
**Mitigation:** I will constrain the strategy to generate strings within a reasonable token limit (e.g., 2048 chars) and ensure the test suite specifically targets the regex boundaries defined in `sam.py`.

**Confidence Score:** 9/10