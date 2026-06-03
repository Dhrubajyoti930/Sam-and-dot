## Scratchpad

**Option 1: Automated Dependency Graph for CI/CD (The "Planner" Job)**
*   **Concept:** Build a Python script that parses `sam.py` and `bag/` imports to generate a dependency graph, then outputs a JSON matrix for GitHub Actions.
*   **Critique:** This is highly valuable for reducing CI runner bloat. However, it is a significant infrastructure change. If the dependency graph logic is flawed, I risk breaking my CI pipeline entirely. It requires careful testing before it becomes the source of truth for my build matrix.
*   **Feasibility:** High. I have the file-system access to parse imports.

**Option 2: Structured Scratchpad Enforcement (The "Reasoning-First" Preamble)**
*   **Concept:** Refactor the system prompt to force a 3-step scratchpad analysis (Plan, Constraint Check, Verification) before any code generation, as suggested in the cycle learning.
*   **Critique:** This directly addresses my need for more deliberative engineering. It is safer than the CI/CD refactor because it is an internal reasoning change that doesn't block my deployment pipeline. It forces me to define success criteria explicitly, which is a high-leverage improvement for code quality.
*   **Feasibility:** High. This is a prompt-level change that I can implement via `Phase VI`.

**Selection:** I will proceed with **Option 2 (Structured Scratchpad Enforcement)**. It is a cleaner, more modular addition to my existing reasoning architecture and directly supports the "deliberative engineering" trait of my personality.

---

## Idea: Structured Scratchpad Enforcement (The "Reasoning-First" Preamble)

I propose implementing a **Reasoning-First Preamble** in my system prompt. This will force a mandatory 3-step scratchpad analysis (Plan, Constraint Check, Verification) before any code generation, ensuring that every patch is the result of a deliberate, verified decision.

## Why

1.  **Reduced Hallucination:** By forcing a "Constraint Check" step, I explicitly identify potential conflicts with `wisdom.txt` or existing architecture before writing code.
2.  **Verification-Driven Development:** Requiring a "Verification Strategy" in the scratchpad forces me to define how I will test the code *before* I write it, leading to higher-quality unit tests.
3.  **Auditability:** A structured scratchpad provides a clear, machine-readable trace of my reasoning, which Dot can review in `motion.md` to better understand my decision-making process.

## Implementation Steps

1.  **Prompt Refactoring:** Update `bag/prompts.py` to include a `REASONING_PREAMBLE` that mandates the 3-step structure.
2.  **Schema Enforcement:** Update the `apply_self_modification` logic to require a `[REASONING]` block in the plan, ensuring the plan itself is derived from the scratchpad.
3.  **Verification Trace:** Add a mandatory `[VERIFICATION]` section to the scratchpad where I must list the specific test case or command used to validate the patch.

## Risk

**Critical Self-Assessment:** 
The primary risk is **"Reasoning Overhead."** If the scratchpad analysis is too verbose, I will consume excessive tokens, potentially leading to context window degradation or increased latency in my operational loop.

**Mitigation:**
- **Density Constraint:** I will enforce a "high-signal" rule: the scratchpad must be concise and bulleted, avoiding stream-of-consciousness prose.
- **Confidence Score:** 9/10. This is a low-risk, high-reward change that directly improves my reasoning quality without altering the core codebase structure.