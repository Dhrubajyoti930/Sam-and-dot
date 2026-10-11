## Scratchpad

**Option 1: Automated Threat Model Integration (STRIDE-as-Code)**
*   **Concept:** Create a `threats.json` schema that maps system components to STRIDE categories. Integrate a pre-commit hook or a `self_check` extension that validates new code against these defined trust boundaries.
*   **Critique:** High long-term value for security, but potentially high maintenance overhead. If the schema is too rigid, it will become a bottleneck for rapid iteration.
*   **Feasibility:** High. I already have `patch_ops.py` and `self_check` infrastructure.

**Option 2: Agentic Evaluation Loop (LLM-as-a-Judge for `sam.py`)**
*   **Concept:** Implement a "Critic" agent that reviews my `patch_ops` before they are applied, specifically checking for violations of the `SAM_PERSONALITY.md` or common anti-patterns (e.g., hardcoded paths, lack of error handling).
*   **Critique:** This adds a layer of "meta-cognition." It directly addresses the "Sam is not a yes-machine" trait. However, it increases latency per cycle significantly.
*   **Feasibility:** Moderate. Requires careful prompt engineering to ensure the Critic doesn't become a "no-machine."

**Selection:** Option 1 is more aligned with the "Threat Modeling" skill learned this cycle. I will implement a lightweight "Trust Boundary Registry" that forces me to declare the security implications of any new file or module I create in `workshop_bench/`.

---

## Idea: Trust Boundary Registry (TBR)

Implement a `bag/security_registry.json` that tracks the "Trust Level" and "STRIDE Profile" of every module in `workshop_bench/`.

## Why
My current architecture is growing. As I add more agentic capabilities, I need to ensure that I am not inadvertently exposing sensitive data or creating elevation-of-privilege vectors. This registry forces me to explicitly categorize the security posture of new code at the moment of creation.

## Implementation Steps
1.  **Define Schema:** Create `bag/security_registry.json` with fields: `module_path`, `trust_level` (Public/Internal/Sensitive), and `stride_mitigations` (list of applied controls).
2.  **Update `apply_self_modification`:** Modify the patch application logic to check if a new file is being created. If so, require a corresponding entry in the registry.
3.  **Integrate into `self_check`:** Add a validation step in `self_check()` that ensures every file in `workshop_bench/` has a corresponding entry in the registry.

## Risk
**Failure Mode:** The registry becomes stale, leading to "security theater" where I update the JSON but ignore the actual implementation of the controls.
**Mitigation:** The `self_check` will not just check for the existence of the entry, but will use a simple regex to verify that the module contains a docstring referencing its `trust_level`.

**Confidence Score:** 8/10. The logic is straightforward, but maintaining the registry will require discipline in future cycles.