import hashlib
import re
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "vector_db" / "semantic_cache.db"
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


def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "CREATE TABLE IF NOT EXISTS cache "
        "(prompt_hash TEXT PRIMARY KEY, response TEXT, cycle INTEGER, embedding BLOB)"
    )
    return conn


def _prompt_hash(prompt: str, cycle: int) -> str:
    normalised = re.sub(r"\[cycle=\d+\s+pv=\d+\]\s*", "", prompt).strip()
    return hashlib.sha256(f"{cycle}:{normalised}".encode()).hexdigest()


def check_cache(prompt: str, current_cycle: int):
    if _is_phase_vi_prompt(prompt):
        return None
    conn = get_db()
    cursor = conn.execute(
        "SELECT response FROM cache WHERE prompt_hash = ? AND cycle >= ?",
        (_prompt_hash(prompt, current_cycle), current_cycle - 5),
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def update_cache(prompt: str, response: str, cycle: int):
    if _is_phase_vi_prompt(prompt):
        return
    prompt_hash = _prompt_hash(prompt, cycle)
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO cache VALUES (?, ?, ?)",
        (prompt_hash, response, cycle),
    )
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM cache").fetchone()[0]
    if count > _MAX_CACHE_ENTRIES:
        conn.execute(
            "DELETE FROM cache WHERE prompt_hash NOT IN "
            "(SELECT prompt_hash FROM cache ORDER BY cycle DESC LIMIT ?)",
            (_MAX_CACHE_ENTRIES,),
        )
        conn.commit()
    conn.close()


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
