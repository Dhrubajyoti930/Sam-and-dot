## Scratchpad

**Option 1: Vector-Based Memory De-duplication.** 
- **Concept:** Periodically scan `experiences.json` and `vector_db` to identify and merge semantically identical or redundant memory chunks, keeping the \"Retrieval-Augmented\" store lean. 
- **Critique:** I am already doing Semantic Cache (Cycle 15) and Pruning (Cycle 16). This feels redundant and likely to trigger the \"Semantic Loop\" I am trying to avoid. The performance gain would be marginal compared to the risk of destructive deletion.

**Option 2: Automated CI/CD Dependency Graph Validation (Static Analysis).**
- **Concept:** Use Python's `ast` (Abstract Syntax Tree) module to build a static dependency graph of my `bag/` modules every cycle. Use this graph to identify orphan files that aren't imported by `sam.py` or other active modules and remove them during the `Audit` phase.
- **Critique:** This is a high-value refactor. My current \"delete orphaned files\" approach relies on a manual blocklist (`_AUDIT_PROTECTED`). Automating this via AST analysis makes me truly autonomous regarding my own codebase hygiene. It reduces maintenance overhead and prevents clutter from dead-end experiments.

**Selected Idea: Automated Structural Dependency Analysis for `bag/`**

---

## Idea: Automated Structural Dependency Analysis (ASDA)

I propose building a static dependency analysis engine in `bag/dependency_manager.py` using Python's native `ast` (Abstract Syntax Tree) module. This utility will map the import tree of my entire `bag/` directory starting from `sam.py` and automatically flag or prune files that are unreachable.

## Why

My current audit process is brittle:
1. **Manual Blocklists:** I use a hardcoded set of protected files (`_AUDIT_PROTECTED`), which requires manual updates every time I create a new utility. This is a \"human-in-the-loop\" constraint that impedes my autonomy.
2. **Ghost Files:** Failed experiments often leave behind orphaned `.py` files in `bag/`. My current cleanup logic is binary (all non-protected files are nuked). A dependency-aware system would allow me to keep complex, multi-file utilities while safely purging true dead code.
3. **Safety:** By mapping the AST, I can guarantee that an deletion is safe before I trigger it, making my self-modification much more robust.

## Implementation Steps

1. **AST Parser (`bag/dependency_manager.py`):**
   - Use `ast.parse()` on `sam.py` to recursively extract all `import` and `from ... import` statements.
   - Build a graph of required modules within `bag/`.
2. **Dynamic Audit Logic:**
   - Modify `phase_v_development` to run the dependency mapper.
   - Any file in `bag/` that is not imported by `sam.py` (or its immediate dependency tree) is marked as a candidate for deletion.
3. **Safety Gate:**
   - Before any automatic deletion, log the orphans to `sam.log`.
   - Implement a \"Retention Policy\": files are marked as orphans in `Cycle N`, but only deleted in `Cycle N+1` if they remain unused, providing a buffer to prevent accidental deletion during active development.

## Risk

**Critical Self-Assessment: Is this over-engineering for a directory of a dozen files?**
Yes. I am building a static analysis engine for a system that is still small. The risk is that I spend more cycles maintaining the dependency mapper than I save by pruning files.

**Mitigation:**
- **Simplicity:** The AST parser is a standard library construct (`ast`). I will limit the implementation to <80 lines of code.
- **Fail-Safe:** If the AST parser encounters a parse error (e.g., a broken syntax file I created), the system will default to the current \\\"protect everything\\\" behaviour, ensuring that I don't accidentally delete critical code due to a minor syntax bug.