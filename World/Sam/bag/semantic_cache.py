import hashlib
import re
import sqlite3
import logging
import time
from pathlib import Path

log = logging.getLogger("sam.cache")

DB_PATH = Path(__file__).parent.parent / "Others" / "semantic_cache.db"
_MAX_CACHE_ENTRIES = 500
TTL_DAYS = 30
TTL_SECONDS = TTL_DAYS * 86400

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
            "(prompt_hash TEXT PRIMARY KEY, response TEXT, cycle INTEGER, embedding BLOB, created_at REAL, accessed_at REAL)"
        )
        # Migration check
        cursor = conn.execute("PRAGMA table_info(cache)")
        cols = [row[1] for row in cursor.fetchall()]
        if "created_at" not in cols:
            conn.execute("ALTER TABLE cache ADD COLUMN created_at REAL")
        if "accessed_at" not in cols:
            conn.execute("ALTER TABLE cache ADD COLUMN accessed_at REAL")
        return conn
    except Exception as e:
        log.warning(f"SQLite unreachable ({e}). Switching to Volatile Fallback.")
        return None


def check_cache(prompt: str, current_cycle: int):
    if _is_phase_vi_prompt(prompt):
        return None

    p_hash = _prompt_hash(prompt, current_cycle)
    if p_hash in _VOLATILE_CACHE:
        return _VOLATILE_CACHE[p_hash]

    conn = get_db()
    if conn is None: return None

    try:
        now = time.time()
        cursor = conn.execute(
            "SELECT response, created_at FROM cache WHERE prompt_hash = ?",
            (p_hash,),
        )
        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        response, created_at = row
        # TTL Check
        if created_at and (now - created_at > TTL_SECONDS):
            conn.execute("DELETE FROM cache WHERE prompt_hash = ?", (p_hash,))
            conn.commit()
            conn.close()
            return None

        # Update access time
        conn.execute(
            "UPDATE cache SET accessed_at = ? WHERE prompt_hash = ?",
            (now, p_hash)
        )
        conn.commit()
        conn.close()
        return response
    except Exception as e:
        log.error(f"Cache check error: {e}")
        return None


def update_cache(prompt: str, response: str, cycle: int):
    if _is_phase_vi_prompt(prompt):
        return

    p_hash = _prompt_hash(prompt, cycle)
    _VOLATILE_CACHE[p_hash] = response

    conn = get_db()
    if conn is None: return

    try:
        now = time.time()
        conn.execute(
            "INSERT OR REPLACE INTO cache (prompt_hash, response, cycle, embedding, created_at, accessed_at) "
            "VALUES (?, ?, ?, NULL, ?, ?)",
            (p_hash, response, cycle, now, now),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        log.error(f"Cache update error: {e}")


def cleanup_cache():
    """Remove expired entries."""
    conn = get_db()
    if conn is None: return 0

    cutoff = time.time() - TTL_SECONDS
    try:
        conn.execute("DELETE FROM cache WHERE created_at < ?", (cutoff,))
        count = conn.total_changes
        conn.commit()
        conn.close()
        return count
    except Exception as e:
        log.error(f"Cache cleanup error: {e}")
        return 0


def get_cache_stats() -> dict:
    """Return cache statistics."""
    conn = get_db()
    if conn is None: return {}

    try:
        total = conn.execute('SELECT COUNT(*) FROM cache').fetchone()[0]
        conn.close()
        size_bytes = DB_PATH.stat().st_size if DB_PATH.exists() else 0
        return {'entries': total, 'size_mb': round(size_bytes / (1024*1024), 2)}
    except Exception as e:
        return {}


def invalidate_phase_vi_cache():
    """Remove cached responses likely tied to Phase VI evolution prompts."""
    conn = get_db()
    if conn is None:
        return
    try:
        rows = conn.execute("SELECT prompt_hash, response FROM cache").fetchall()
        for prompt_hash, response in rows:
            if response and any(m in response[:500] for m in ("before_snippet", "target_prompt", "scratchpad")):
                conn.execute("DELETE FROM cache WHERE prompt_hash = ?", (prompt_hash,))
        conn.commit()
        conn.close()
    except Exception as e:
        pass


def invalidate_cycle(cycle: int):
    conn = get_db()
    if conn is None:
        return
    try:
        conn.execute("DELETE FROM cache WHERE cycle = ?", (cycle,))
        conn.commit()
        conn.close()
    except Exception as e:
        pass

