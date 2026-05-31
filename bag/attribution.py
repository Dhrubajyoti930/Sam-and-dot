
"""
bag/attribution.py — Grounded Attribution Layer
Provides semantic similarity scoring for architectural planning.
"""
import difflib
from pathlib import Path

def get_similarity(assertion: str, context: str) -> float:
    """Calculate basic similarity ratio."""
    return difflib.SequenceMatcher(None, assertion.lower(), context.lower()).ratio()

def verify_assertion(assertion: str, wisdom_path: Path) -> float:
    if not wisdom_path.exists(): return 0.0
    wisdom = wisdom_path.read_text()
    return get_similarity(assertion, wisdom)