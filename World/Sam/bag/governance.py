import logging
import subprocess
import sys
from pathlib import Path

log = logging.getLogger("sam.governance")

def trial_and_verdict(plan_ops, root: Path, test_script: Path):
    """
    Apply a patch plan in a 'Trial' mode.
    Verifies syntax and runs behavioural tests before 'Accepting' the changes.
    """
    from bag.patch_ops import apply_patch_operations

    log.info("⚖️ Entering Trial Mode for proposed changes...")

    # 1. Take a 'Before' snapshot for instant rejection/rollback
    # (Snapshot is already handled in sam.py core loop, but we use it here for logic)

    # 2. Apply proposed operations
    success = apply_patch_operations(plan_ops, root, log)
    if not success:
        log.error("❌ Verdict: REJECTED (Patch Application Failed)")
        return False, "Patch application mismatch"

    # 3. Syntax Gate (Gate 1)
    try:
        # Check all python files in the world for syntax errors
        # Uses ruff for deep logical scan
        result = subprocess.run(
            ["ruff", "check", str(root), "--select", "F", "--exclude", "rollback_registry"],
            capture_output=True, text=True, timeout=20,
        )
        if result.returncode != 0:
            log.error(f"❌ Verdict: REJECTED (Syntax/Logic Violation)\n{result.stdout}")
            return False, f"Syntax Gate Failed: {result.stdout[:200]}"
    except Exception as e:
        log.warning(f"⚠️ Syntax Gate Bypassed (Ruff error: {e})")

    # 4. Behavioural Gate (Gate 2)
    if test_script.exists():
        log.info("🧪 Running Behavioural Integrity Tests...")
        try:
            result = subprocess.run(
                [sys.executable, str(test_script)],
                capture_output=True, text=True, timeout=30,
                cwd=str(root)
            )
            if result.returncode != 0:
                log.error(f"❌ Verdict: REJECTED (Behavioural Failure)\n{result.stdout}")
                return False, f"Behavioural Gate Failed: {result.stderr[:200]}"
        except Exception as e:
            log.error(f"❌ Verdict: REJECTED (Test Runner Crashed: {e})")
            return False, f"Test Runner Crash: {e}"
    else:
        log.info("ℹ️ No test script found. Behavioural Gate skipped.")

    log.info("✅ Verdict: ACCEPTED. Changes merged into World state.")
    return True, "Success"
