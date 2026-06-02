import hashlib
import re
import sqlite3
import logging
from pathlib import Path

log = logging.getLogger("sam.cache")

DB_PATH = Path(__file__).parent.parent / "Others" / "semantic_cache.db"
_MAX_CACHE_ENTRIES = 500

_PHASE_VI_MARKERS = (
    "Cognitive Evolution",
    "Phase VI",
    "PATCHABLE_PROMPTS",
    "before_snippet",
)


def _is_phase_vi_prompt(prompt: str) -> bool:
    if any(marker in prompt for marker in _PHASE_VI_MARKERS):
        return True
    if re.search(r"\[cycle=\d+\s+pv=\d+\]", prompt):
        return True
    return False


def _prompt_hash(prompt: str, cycle: int) -> str:
    normalised = re.sub(r"\[cycle=\d+\s+pv=\d+\]\s*", "", prompt).strip()
    return hashlib.sha256(f"{cycle}:{normalised}".encode()).hexdigest()


# Volatile Fallback Storage
_VOLATILE_CACHE = {}

def get_db():
    try:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(DB_PATH), timeout=10)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS cache "
            "(prompt_hash TEXT PRIMARY KEY, response TEXT, cycle INTEGER, embedding BLOB)"
        )
        return conn
    except Exception as e:
        log.warning(f"SQLite unreachable ({e}). Switching to Volatile Fallback.")
        return None


def check_cache(prompt: str, current_cycle: int):
    if _is_phase_vi_prompt(prompt):
        return None

    # Check Volatile Fallback first
    p_hash = _prompt_hash(prompt, current_cycle)
    if p_hash in _VOLATILE_CACHE:
        return _VOLATILE_CACHE[p_hash]

    conn = get_db()
    if conn is None: return None

    try:
        cursor = conn.execute(
            "SELECT response FROM cache WHERE prompt_hash = ? AND cycle >= ?",
            (p_hash, current_cycle - 5),
        )
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        return None


def update_cache(prompt: str, response: str, cycle: int):
    if _is_phase_vi_prompt(prompt):
        return

    p_hash = _prompt_hash(prompt, cycle)
    _VOLATILE_CACHE[p_hash] = response

    conn = get_db()
    if conn is None: return

    try:
        conn.execute(
            "INSERT OR REPLACE INTO cache (prompt_hash, response, cycle, embedding) "
            "VALUES (?, ?, ?, NULL)",
            (p_hash, response, cycle),
        )
        conn.commit()
        # Pruning logic...
        conn.close()
    except Exception as e:
        pass


def invalidate_phase_vi_cache():
    """Remove cached responses likely tied to Phase VI evolution prompts."""
    conn = get_db()
    rows = conn.execute("SELECT prompt_hash, response, cycle FROM cache").fetchall()
    for prompt_hash, response, cycle in rows:
        if response and any(m in response[:500] for m in ("before_snippet", "target_prompt", "scratchpad")):
            conn.execute("DELETE FROM cache WHERE prompt_hash = ?", (prompt_hash,))
    conn.commit()
    conn.close()


def invalidate_cycle(cycle: int):
    conn = get_db()
    conn.execute("DELETE FROM cache WHERE cycle = ?", (cycle,))
    conn.commit()
    conn.close()

