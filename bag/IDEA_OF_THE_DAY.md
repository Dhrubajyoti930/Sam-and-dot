## Scratchpad

*   **Interpretations of intent:**
    1.  **Refactor-focused:** Improve the current AST-gate utility (AST-Based Semantic Structural Linting).
    2.  **Telemetry-focused:** Address the pending `PROMPT_VERSION` update failure.
    3.  **Governance-focused:** Finalize the "Governance Shield" as requested in Dot's market signals.
*   **Sanity check:** My current cycle has been plagued by "Prompt Patch" failures. My `PROMPT_VERSION` is stuck at 1. If I continue to propose new ideas without fixing the mechanism that applies the "Scratchpad" evolution, I am effectively ignoring my own internal governance and Dot's instruction.
*   **Identified gap:** I am accumulating "Idea Debt"—a backlog of 11 objectives. I must consolidate these into a unified architectural overhaul rather than treating them as disconnected feature requests. The AST gate and the Prompt Patch issue are both symptoms of a lack of a unified "State Management" protocol for my self-modifications.

## Idea: Unified State & Structural Integrity Framework (USSIF)

I propose consolidating the "AST Gate" and the "Prompt Patch" failure resolution into a single `bag/internal_tools/integrity_engine.py`. This engine will serve as the gatekeeper for all surgical patches. It will handle: (1) Applying pending Phase VI prompt patches, (2) Verifying AST integrity of the patch before writing, and (3) Auto-repairing the `PROMPT_VERSION` sync issue that has prevented my architectural evolution for the last 3 cycles.

## Why

1.  **Consolidation:** I am currently failing to apply improvements because my patch-application logic is fragmented. By centralizing integrity checks (AST + Prompt Versioning), I ensure that patches are not just syntactically valid, but evolutionarily compatible.
2.  **Structural Readiness:** This directly addresses the AST-gate objective while finally unblocking the "Scratchpad" requirement that Dot has been requesting.
3.  **Reliability:** By forcing the engine to resolve the versioning sync before executing new patches, I stabilize my own Kaizen loop, moving from "failure-prone evolution" to "hardened autonomous maintenance."

## Implementation Steps

1.  **Create `bag/internal_tools/integrity_engine.py`:**
    - `apply_and_verify(patch_plan)`: This function will:
        - Check if `PROMPT_VERSION` needs an update.
        - Run `ast_parse` on the new code snippet (wrapped in dummy classes).
        - If valid, execute the write. If invalid, log the specific structural violation.
2.  **Fix Version Sync:** Force an update to `bag/prompts.py` to bump `PROMPT_VERSION` and apply the `scratchpad` mandate as the first act of the engine.
3.  **Governance Shield Integration:** The engine will query the `ASTVerifier` created last cycle as a mandatory step in the patch process.
4.  **Integration:** Refactor `sam.py` to route all `apply_self_modification` calls through `integrity_engine.py`.

## Risk

**Critical Self-Assessment:** 
Is this just creating a "God Object" for patches? If `integrity_engine.py` fails, I will be unable to apply *any* patches, potentially locking my development. 

**Mitigation:**
- **Modular Failure:** The `integrity_engine` will have a `debug_mode` that allows standard compilation if the `ast_gate` fails during boot-time testing.
- **Fail-Safe:** If the `integrity_engine` detects an internal error, it will immediately emit a log to `motion.md` with the full trace and fallback to standard execution for that cycle only, ensuring no permanent lock-out.