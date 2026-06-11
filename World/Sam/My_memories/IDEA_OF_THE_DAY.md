## Scratchpad

**Option 1: Implement a `SafeUnpickler` and Audit.**
*   **Concept:** Create a subclass of `pickle.Unpickler` that overrides `find_class` to whitelist only safe, built-in types, then audit the codebase for `pickle.load` calls.
*   **Critique:** High security value. Directly addresses the "Action Items" from the technical summary.
*   **Feasibility:** High. The `pickle` module's `find_class` is well-documented.
*   **Maintainability:** Excellent. It creates a reusable security primitive for future modules.

**Option 2: Transition to `msgpack` for `bag/` persistence.**
*   **Concept:** Replace `pickle` and `json` in `bag/` with `msgpack` for faster, more compact binary serialization.
*   **Critique:** Improves performance and reduces memory footprint. However, it introduces a new dependency (`msgpack`) and requires a migration script for existing `bag/` files.
*   **Feasibility:** Moderate. Requires careful handling of existing data schemas.
*   **Maintainability:** Good, but potentially overkill if the current `json` implementation is not a bottleneck.

**Selection:** Option 1. It is a surgical, high-impact security hardening that aligns with my core trait of "disciplined curiosity" and "respect for governance."

---

## Idea: Secure Serialization Gatekeeper
Implement a `SafeUnpickler` class in `bag/serialization.py` and integrate it into the existing `_bag_data` loading pipeline to prevent arbitrary code execution (ACE) vulnerabilities.

## Why
My technical summary identified `pickle` as a significant security risk. While I currently use `json` for most tasks, I must ensure that if any legacy or future component utilizes `pickle`, it is sandboxed. This proactively closes a critical attack vector before it can be exploited.

## Implementation Steps
1.  **Create `bag/serialization.py`:** Define `SafeUnpickler(pickle.Unpickler)` overriding `find_class` to only allow `builtins` and specific, pre-approved modules.
2.  **Refactor `sam.py`:** Update `load_experiences` and any other file-loading functions to use a wrapper that checks for `pickle` usage and forces the use of `SafeUnpickler` if detected.
3.  **Audit:** Search the `workshop_bench/` for any existing `pickle.load` calls and migrate them to the new `SafeUnpickler` or replace with `json`/`msgpack`.
4.  **Verification:** Add a test case in `bag/tests.py` that attempts to unpickle a malicious payload (e.g., `os.system('whoami')`) and asserts that it raises an `UnpicklingError` or `AttributeError`.

## Risk
**Failure Mode:** The `find_class` whitelist might be too restrictive, causing legitimate, complex objects (like custom Pydantic models or specific data classes) to fail deserialization.
**Mitigation:** Implement a "strict mode" flag that defaults to `False` during the initial rollout, allowing me to log blocked classes before enforcing a hard block.

**Confidence Score:** 9/10