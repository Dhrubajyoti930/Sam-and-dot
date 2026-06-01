import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "vector_db" / "semantic_cache.db"

def compact_cache():
    """Prune low-utility entries from semantic cache."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        conn.execute("ALTER TABLE cache ADD COLUMN pinned INTEGER DEFAULT 0")
        conn.execute("ALTER TABLE cache ADD COLUMN last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        conn.execute("ALTER TABLE cache ADD COLUMN hit_count INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        pass
    
    conn.execute("""
        DELETE FROM cache 
        WHERE pinned = 0 
        AND (hit_count * 2 - (julianday('now') - julianday(last_accessed)) * 12) < -5
    """)
    conn.commit()
    conn.close()