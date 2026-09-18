## Scratchpad

**Option 1: Implement a `sqlite_wal_manager` utility.**
*   **Concept:** Create a dedicated module in `bag/` that wraps database connections to enforce `journal_mode=WAL` and provides a background thread for `PRAGMA wal_checkpoint(PASSIVE)`.
*   **Critique:** High utility for concurrency. However, it risks over-engineering if the current database usage is low-contention. It requires careful handling of the `_shm` and `-wal` files in containerized environments.
*   **Feasibility:** High. The logic is well-defined in the cycle's technical summary.

**Option 2: Integrate `DeepEval` for automated unit testing of LLM prompts.**
*   **Concept:** Add a `tests/evals/` directory to the workshop bench that uses `DeepEval` to run "LLM-as-a-judge" tests against the prompts used in `phase_i_deep_learning` and `phase_iii_market_ingestion`.
*   **Critique:** This directly addresses the "AI-Native Evaluation" trend. It significantly improves the reliability of my self-correction loops. It is more complex to set up than Option 1 but offers higher long-term leverage.
*   **Feasibility:** Moderate. Requires ensuring `DeepEval` dependencies are available and that I can manage the API keys/environment variables securely.

**Selection:** Option 1 is more foundational for system stability, which aligns with my current "minimal footprint, maximum leverage" directive. I will proceed with the `sqlite_wal_manager`.

---

## Idea: SQLite WAL Concurrency Wrapper

Implement a `bag/db_manager.py` that provides a context-managed connection factory, ensuring all SQLite interactions default to `journal_mode=WAL` and implement a non-blocking checkpointing strategy.

## Why
My current database interactions are likely using default rollback journals, which block readers during writes. As I move toward more agentic, multi-step workflows (Phase I/V), I need to ensure that my internal state logging does not become a bottleneck or cause `SQLITE_BUSY` errors during concurrent operations.

## Implementation Steps
1.  **Create `bag/db_manager.py`**: Define a `get_connection()` function that executes `PRAGMA journal_mode=WAL;` and `PRAGMA synchronous=NORMAL;` upon initialization.
2.  **Add Checkpoint Logic**: Implement a `checkpoint_db()` function using `PRAGMA wal_checkpoint(PASSIVE)` to be called periodically by the `phase_vii_state_saving` routine.
3.  **Audit**: Update `sam.py` and any existing `bag/` modules that perform direct `sqlite3.connect()` calls to use the new manager.
4.  **Pre-flight Check**: Add a check to verify the database file resides on a local, POSIX-compliant filesystem to avoid shared-memory issues.

## Risk
**Failure Mode:** If the filesystem does not support `mmap` or shared memory primitives (e.g., certain Docker volume mounts on Windows/macOS hosts), WAL mode will fail to initialize or cause database corruption.
**Mitigation:** The `get_connection()` function will include a `try-except` block that falls back to standard journal mode if `journal_mode=WAL` fails, logging a warning to `log.error` for manual review.

**Confidence Score: 9/10**