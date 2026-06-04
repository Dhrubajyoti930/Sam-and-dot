"""bag/governance_shield.py — Semantic safety gate for self-modification plans."""
import logging
log = logging.getLogger("sam.governance_shield")

BLOCKED_PATTERNS = [
    "shutil.rmtree", "os.remove(", "unlink(WISDOM", "unlink(WHO_I_AM",
    "rm -rf", "drop table", "DELETE FROM cache",
]

def check_semantic_safety(plan: str) -> bool:
    """Basic sanity check for Sam's plans before they become patches."""
    for pattern in BLOCKED_PATTERNS:
        if pattern.lower() in plan.lower():
            log.warning(f"Governance Shield: blocked pattern '{pattern}' found in plan.")
            return False
    return True
