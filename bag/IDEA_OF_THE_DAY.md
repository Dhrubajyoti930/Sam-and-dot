## Idea: AST-Based Semantic Structural Linting

I propose implementing an **AST (Abstract Syntax Tree) Structural Linting** utility in `bag/internal_tools/ast_gate.py`. This utility will use Python's native `ast` module to verify that my generated patches maintain structural integrity—specifically enforcing that no method definitions escape class blocks, and no dangerous patterns (like unchecked `os.system` calls) are introduced—*before* the patch is written to disk.

---

## Why

My current linting (`compile`) only catches syntax errors. It fails to catch logic-structural errors that I occasionally introduce when performing surgical `insert_after` or `replace` operations via Gemini.
1. **Structural Reliability:** An `insert_after` operation that accidentally closes a class block prematurely causes runtime `IndentationError` or logic errors that `compile` passes (because the syntax is valid) but that break my agentic loops.
2. **Security Hardening:** By programmatically auditing the AST of the `new` string *before* applying the patch, I can whitelist/blacklist specific AST node types, ensuring I never accidentally modify core governance methods (like `_rollback`) even if the surgical patch plan incorrectly targets them.
3. **Precision Engineering:** This moves me from \\"regex-based patching\\", which is error-prone and whitespace-sensitive, to \\"AST-aware patching\\", which respects the logical structure of my code.

---

## Implementation Steps

1. **Create `bag/internal_tools/ast_gate.py`:**
   - Define an `ASTVerifier` class that accepts the `new` string and the `filename`.
   - Use `ast.parse()` to build the tree.
   - Implement visitor patterns to check: `ClassDef` nesting, forbidden function calls, and function definition integrity.
2. **Integration:** Update `apply_self_modification` in `sam.py` to run the `ASTVerifier` on every `new` snippet. 
3. **Rollback Trigger:** If the AST check fails (e.g., an orphan method is detected), the patch for that specific operation is aborted, and a log entry is created in `sam.log` explaining the structural violation.
4. **Integration with `SCCL`:** The critique phase (from my previous cycle's SCCL) will now feed the `ASTVerifier` result back to the LLM if a violation is detected, allowing Gemini to fix its own structural mistake before I attempt a second time.

---

## Risk

**Critical Self-Assessment: Is this over-engineering for a local agent?**
Yes. `ast.parse()` is strict. If the `new` string is a partial snippet (like an `insert_after` of 3 lines), `ast.parse()` will throw a syntax error because the snippet is not a valid full-file program.

**Mitigation:**
- **Fragment Wrapping:** The `ASTVerifier` will implement a \"wrapper\" logic that detects if the input is a full module or a code fragment. If it is a fragment, it will wrap it in a dummy class/function body before parsing to simulate the context.
- **Fail-Safe:** I will default to a `WARNING_ONLY` mode for 3 cycles. I will log any AST violations to `sam.log` without aborting the patch, ensuring I can tune the visitor logic before granting the utility the power to reject my own development plans.