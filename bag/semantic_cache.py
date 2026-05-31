import sqlite3
import hashlib

def get_db():
    conn = sqlite3.connect("vector_db/semantic_cache.db")
    conn.execute("CREATE TABLE IF NOT EXISTS cache (prompt_hash TEXT PRIMARY KEY, response TEXT, cycle INTEGER)")
    return conn

def check_cache(prompt: str, current_cycle: int):
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
    conn = get_db()
    cursor = conn.execute("SELECT response FROM cache WHERE prompt_hash = ? AND cycle >= ?", (prompt_hash, current_cycle - 5))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def update_cache(prompt: str, response: str, cycle: int):
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO cache VALUES (?, ?, ?)", (prompt_hash, response, cycle))
    conn.commit()
    conn.close()