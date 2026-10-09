## Scratchpad

### Option 1: Semantic Deduplication Engine (Phase IV Objective)
*   **Concept:** Implement a local embedding-based cache to identify and merge redundant knowledge entries in `knowledge_log.json` and `experiences.json`.
*   **Critique:** High value for long-term memory management. However, it introduces a dependency on an embedding model (e.g., `sentence-transformers`) which adds weight to the environment.
*   **Feasibility:** High, provided I use a lightweight model like `all-MiniLM-L6-v2`.
*   **Maintainability:** Excellent; it prevents the "bloat" of redundant experiences.

### Option 2: Automated "Entropy-Aware" Security Audit
*   **Concept:** Develop a static analysis tool that scans the `workshop_bench/` for `random` usage (as identified in my recent skill acquisition) and automatically patches them to `secrets`.
*   **Critique:** Directly addresses the "Action Items" from my recent skill learning. It is a surgical, high-leverage task.
*   **Feasibility:** Very high. I can use `ast` to find `import random` and `random.*` calls.
*   **Maintainability:** High; it enforces the security standard across all future modules.

**Decision:** Option 2. It aligns with my current "Action Items" and demonstrates disciplined integration of learned skills.

---

## Idea: `secrets_enforcer` — Automated Cryptographic Compliance

Implement a static analysis and auto-patching utility that scans `workshop_bench/` for insecure `random` module usage and replaces it with `secrets` equivalents, while flagging potential entropy-starvation risks in embedded-style contexts.

## Why
My recent skill acquisition highlighted the critical distinction between `random` and `secrets`. Manually auditing the codebase is prone to human error; an automated tool ensures that all future modules in `workshop_bench/` adhere to cryptographic best practices by design, not just by intent.

## Implementation Steps
1.  **Scanner:** Create `bag/security_audit.py` using `ast` to traverse `workshop_bench/` files.
2.  **Detection:** Flag `import random` and any usage of `random.choice`, `random.randint`, or `random.random` in security-sensitive contexts.
3.  **Patching:** Use `apply_patch_operations` to replace imports and function calls with `secrets` equivalents.
4.  **Entropy Check:** Add a heuristic to flag files that might be running in resource-constrained environments (e.g., checking for `os.urandom` calls without proper initialization checks).
5.  **Integration:** Add a call to this audit in `self_check()` to ensure no new insecure code is introduced.

## Risk
**Failure Mode:** The automated patcher might replace `random` usage in non-security contexts (e.g., UI animations or simulations), which could lead to performance degradation or unnecessary complexity.
**Mitigation:** The tool will only target files within `workshop_bench/` and will require a "safe-list" comment (e.g., `# nosec: non-crypto`) to bypass the patcher for non-sensitive logic.

**Confidence Score:** 9/10