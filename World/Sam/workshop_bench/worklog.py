"""
worklog.py — Sam's wandering notebook.

Sam opens an entry when he starts something, updates it if he comes back,
closes it when it's done. Dot notices anything open too long.

Entry schema:
{
    "id":         "cycle-8-profiler",
    "title":      "sys.monitoring profiler",
    "status":     "open" | "wandering" | "closed" | "abandoned",
    "opened_at":  "2026-05-31T15:00:00",
    "opened_cycle": 8,
    "last_touched_at": "2026-05-31T15:00:00",
    "last_touched_cycle": 8,
    "closed_at":  null,
    "updates":    ["note 1", "note 2"],
    "outcome":    null | "applied" | "rolled_back" | "deferred"
}
"""

import json
import datetime
from pathlib import Path

STALE_CYCLES = 4  # Dot flags entries untouched for this many cycles


def _worklog_path() -> Path:
    from bag.bag_paths import resolve
    return resolve(Path(__file__).parent.resolve(), "worklog")


def _load() -> list:
    path = _worklog_path()
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save(entries: list):
    _worklog_path().write_text(json.dumps(entries, indent=2), encoding="utf-8")


def _now() -> str:
    return datetime.datetime.utcnow().isoformat()


def _make_id(cycle: int, title: str) -> str:
    slug = title.lower().replace(" ", "-")[:30].strip("-")
    return f"cycle-{cycle}-{slug}"


def open_entry(cycle: int, title: str, note: str = "") -> str:
    """Sam starts something new. Returns the entry id."""
    entries = _load()
    entry_id = _make_id(cycle, title)

    # Don't duplicate if already open from a previous attempt
    for e in entries:
        if e["id"] == entry_id:
            return entry_id

    entry = {
        "id":                   entry_id,
        "title":                title,
        "status":               "open",
        "opened_at":            _now(),
        "opened_cycle":         cycle,
        "last_touched_at":      _now(),
        "last_touched_cycle":   cycle,
        "closed_at":            None,
        "updates":              [note] if note else [],
        "outcome":              None,
    }
    entries.append(entry)
    _save(entries)
    return entry_id


def update_entry(entry_id: str, cycle: int, note: str):
    """Sam comes back to something. Marks it wandering if it was open."""
    entries = _load()
    for e in entries:
        if e["id"] == entry_id:
            if e["status"] == "open":
                e["status"] = "wandering"
            e["last_touched_at"]    = _now()
            e["last_touched_cycle"] = cycle
            e["updates"].append(note)
            _save(entries)
            return
    # If not found, open it fresh
    open_entry(cycle, entry_id, note)


def close_entry(entry_id: str, cycle: int, outcome: str, note: str = ""):
    """Sam finishes something. outcome: 'applied' | 'rolled_back' | 'deferred'."""
    entries = _load()
    for e in entries:
        if e["id"] == entry_id:
            e["status"]             = "closed"
            e["closed_at"]          = _now()
            e["last_touched_at"]    = _now()
            e["last_touched_cycle"] = cycle
            e["outcome"]            = outcome
            if note:
                e["updates"].append(note)
            _save(entries)
            return


def get_open_entries() -> list:
    """Return all entries that are open or wandering."""
    return [e for e in _load() if e["status"] in ("open", "wandering")]


def get_stale_entries(current_cycle: int) -> list:
    """Return open/wandering entries untouched for STALE_CYCLES or more."""
    return [
        e for e in get_open_entries()
        if current_cycle - e.get("last_touched_cycle", 0) >= STALE_CYCLES
    ]


def stale_report(current_cycle: int) -> str:
    """Plain-text summary of stale entries for Dot to paste into motion.md."""
    stale = get_stale_entries(current_cycle)
    if not stale:
        return ""
    lines = [f"### Worklog — {len(stale)} stale item(s) for Sam\n"]
    for e in stale:
        idle = current_cycle - e.get("last_touched_cycle", 0)
        lines.append(
            f"- **{e['title']}** (id: `{e['id']}`)\n"
            f"  Opened cycle {e['opened_cycle']}, last touched cycle "
            f"{e['last_touched_cycle']} ({idle} cycles ago).\n"
            f"  Last note: {e['updates'][-1] if e['updates'] else '(none)'}\n"
        )
    lines.append(
        "\nSam: pick one of these up this cycle or mark it deferred. "
        "Don't let ideas rot.\n"
    )
    return "\n".join(lines)
