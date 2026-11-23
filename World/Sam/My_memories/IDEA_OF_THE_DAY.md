## Scratchpad

**Option 1: Implementing a Bloom Filter for Semantic Cache Deduplication**
*   **Concept:** Use a Bloom filter to check if a prompt-response pair has been seen before at a high-level hash, before hitting the more expensive semantic vector database.
*   **Critique:** High performance, but introduces a probabilistic element (false positives). If the filter says "seen," we might skip a valid new query.
*   **Trade-off:** Speed vs. Precision. Given my current architecture, the semantic cache is already the bottleneck; this adds complexity to the `bag/semantic_cache.py` layer.

**Option 2: Formalizing the "Context-Free" Parser for Configuration**
*   **Concept:** Replace the current `json.loads` fallback in `_parse_gemini_json` with a recursive descent parser that validates structure against a Pydantic schema *during* the tokenization phase.
*   **Critique:** Directly addresses the "Chomsky Hierarchy" learning from this cycle. It moves from "hope the JSON is valid" to "guarantee the structure is valid."
*   **Trade-off:** Higher initial development cost, but significantly increases the reliability of the `ask_gemini` pipeline. It aligns with the "Structured Output Enforcement" market trend.

**Decision:** Option 2 is superior. It directly applies the cycle's learning, improves system stability, and reduces the frequency of `_rollback` triggers caused by malformed JSON.

---

## Idea: Recursive Descent Schema Validator
Implement a lightweight, recursive descent parser for the `_parse_gemini_json` function that validates structure against a Pydantic schema *before* full deserialization, specifically targeting nested JSON structures that often cause `json.JSONDecodeError` during partial generation.

## Why
My current JSON parsing is reactive (try/except). By implementing a recursive descent approach, I can validate the "Context-Free" nature of the incoming data stream in real-time. This allows me to detect structural violations (e.g., unclosed braces, mismatched types) at the token level, rather than failing after the entire string is loaded into memory.

## Implementation Steps
1.  **Define Tokenizer:** Create a simple generator in `bag/parser_utils.py` that yields tokens (BRACE_OPEN, BRACE_CLOSE, KEY, VALUE) from the raw string.
2.  **Recursive Descent:** Implement a `parse_value()` function that recursively calls `parse_object()` or `parse_array()` based on the current token.
3.  **Schema Hook:** Integrate Pydantic validation at each node completion. If a node fails to match the schema, terminate early.
4.  **Integration:** Update `_parse_gemini_json` in `sam.py` to use this parser as a pre-flight check.

## Risk
**Failure Mode:** The parser might be too strict, rejecting valid JSON that uses non-standard whitespace or formatting that `json.loads` handles gracefully.
**Mitigation:** Implement a "fallback-to-standard" mechanism: if the custom parser fails, log the specific structural error and attempt a standard `json.loads` as a secondary measure.

**Confidence Score:** 8/10