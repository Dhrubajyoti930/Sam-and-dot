import sqlite3
import hashlib
from pathlib import Path

# Fix #4 — absolute path so this works regardless of working directory
DB_PATH = Path(__file__).parent.parent / "vector_db" / "semantic_cache.db"

_MAX_CACHE_ENTRIES = 500  # Fix #11 — cap cache size


def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "CREATE TABLE IF NOT EXISTS cache "
        "(prompt_hash TEXT PRIMARY KEY, response TEXT, cycle INTEGER)"
    )
    return conn


def check_cache(prompt: str, current_cycle: int):
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
    conn = get_db()
    cursor = conn.execute(
        "SELECT response FROM cache WHERE prompt_hash = ? AND cycle >= ?",
        (prompt_hash, current_cycle - 5),
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def update_cache(prompt: str, response: str, cycle: int):
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO cache VALUES (?, ?, ?)",
        (prompt_hash, response, cycle),
    )
    conn.commit()

    # Fix #11 — prune oldest entries beyond the cap
    count = conn.execute("SELECT COUNT(*) FROM cache").fetchone()[0]
    if count > _MAX_CACHE_ENTRIES:
        conn.execute(
            "DELETE FROM cache WHERE prompt_hash NOT IN "
            "(SELECT prompt_hash FROM cache ORDER BY cycle DESC LIMIT ?)",
            (_MAX_CACHE_ENTRIES,),
        )
        conn.commit()

    conn.close()
