"""Surgical patch application shared by Phase V and Phase VI."""

import difflib
from pathlib import Path

from bag.workshop_paths import FORBIDDEN_BASENAMES, is_allowed_patch_filename

# Minimum similarity ratio for fuzzy 'old' / 'anchor' matching.
# High enough to avoid false positives, low enough to absorb typical
# Gemini hallucinations (missing punctuation, wrong em-dash, extra spaces).
FUZZY_THRESHOLD = 0.88


def _normalize(s: str) -> str:
    """Collapse all whitespace for fuzzy comparison."""
    return " ".join(s.split())


def _find_fuzzy_match(needle: str, source: str) -> tuple[str | None, float]:
    """Find the best-matching block in source for needle.

    Slides a window of len(needle_lines) over source_lines, comparing
    whitespace-normalized flat strings so minor Gemini hallucinations
    (dropped punctuation, wrong em-dash, extra spaces) still match.

    Returns (original_source_block, ratio) or (None, best_ratio) if no
    window clears FUZZY_THRESHOLD.
    """
    needle_lines = needle.splitlines()
    source_lines = source.splitlines()
    n = len(needle_lines)
    if n == 0 or n > len(source_lines):
        return None, 0.0

    needle_flat = " | ".join(_normalize(l) for l in needle_lines)

    best_ratio = 0.0
    best_start = -1

    for i in range(len(source_lines) - n + 1):
        window_flat = " | ".join(_normalize(l) for l in source_lines[i : i + n])
        ratio = difflib.SequenceMatcher(None, needle_flat, window_flat).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_start = i

    if best_ratio >= FUZZY_THRESHOLD and best_start >= 0:
        return "\n".join(source_lines[best_start : best_start + n]), best_ratio
    return None, best_ratio


def apply_patch_operations(operations: list, root: Path, log) -> bool:
    """Apply replace / insert_after / delete ops. Returns True if any succeeded.

    'old' and 'anchor' strings are matched with fuzzy whitespace-normalised
    comparison (threshold 0.88) so minor Gemini hallucinations don't silently
    discard the operation. When a fuzzy match is used the log notes the ratio.
    """
    applied = []
    created = []  # track newly created files for rollback cleanup
    # Guard: Gemini sometimes returns strings mixed into the array — skip them
    operations = [op for op in operations if isinstance(op, dict)]
    if not operations:
        log.warning("No valid patch operations found (all entries were non-dict).")
        apply_patch_operations._last_created = []
        return False

    for op in operations:
        fname = op.get("filename", "")
        operation = op.get("operation", "")

        if not is_allowed_patch_filename(fname):
            log.warning(f"Blocked patch to '{fname}' — outside allowed scope.")
            continue

        basename = Path(fname).name
        if basename in FORBIDDEN_BASENAMES:
            log.warning(f"Blocked patch to governance file '{fname}'.")
            continue

        if "content" in op:
            log.warning(f"Blocked full-file rewrite on '{fname}' — 'content' key forbidden.")
            continue

        target = root / fname
        if not target.exists():
            if operation == "insert_after":
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(op.get("new", ""))
                log.info(f"Created new file via insert_after → {fname}")
                applied.append(fname)
                created.append(str(target))
            else:
                log.warning(f"Skipping patch on non-existent file '{fname}'.")
            continue

        source = target.read_text(encoding="utf-8")

        if operation == "replace":
            old, new = op.get("old", ""), op.get("new", "")
            if not old:
                log.warning(f"replace on '{fname}': 'old' is empty — skipping.")
                continue

            if old in source:
                # Exact match — fast path
                target.write_text(source.replace(old, new, 1), encoding="utf-8")
                log.info(f"Applied replace (exact) → {fname}")
                applied.append(fname)
            else:
                # Fuzzy fallback
                match, ratio = _find_fuzzy_match(old, source)
                if match:
                    log.info(f"Applied replace (fuzzy {ratio:.2f}) → {fname}")
                    target.write_text(source.replace(match, new, 1), encoding="utf-8")
                    applied.append(fname)
                else:
                    log.warning(
                        f"replace on '{fname}': 'old' not found (best fuzzy={ratio:.2f}) — skipping."
                    )

        elif operation == "insert_after":
            anchor, new = op.get("anchor", ""), op.get("new", "")
            if not anchor:
                log.warning(f"insert_after on '{fname}': 'anchor' is empty — skipping.")
                continue

            if anchor in source:
                target.write_text(source.replace(anchor, anchor + "\n" + new, 1), encoding="utf-8")
                log.info(f"Applied insert_after (exact) → {fname}")
                applied.append(fname)
            else:
                match, ratio = _find_fuzzy_match(anchor, source)
                if match:
                    log.info(f"Applied insert_after (fuzzy {ratio:.2f}) → {fname}")
                    target.write_text(
                        source.replace(match, match + "\n" + new, 1), encoding="utf-8"
                    )
                    applied.append(fname)
                else:
                    log.warning(
                        f"insert_after on '{fname}': anchor not found (best fuzzy={ratio:.2f}) — skipping."
                    )

        elif operation == "delete":
            old = op.get("old", "")
            if not old:
                log.warning(f"delete on '{fname}': 'old' is empty — skipping.")
                continue

            if old in source:
                target.write_text(source.replace(old, "", 1), encoding="utf-8")
                log.info(f"Applied delete (exact) → {fname}")
                applied.append(fname)
            else:
                match, ratio = _find_fuzzy_match(old, source)
                if match:
                    log.info(f"Applied delete (fuzzy {ratio:.2f}) → {fname}")
                    target.write_text(source.replace(match, "", 1), encoding="utf-8")
                    applied.append(fname)
                else:
                    log.warning(
                        f"delete on '{fname}': 'old' not found (best fuzzy={ratio:.2f}) — skipping."
                    )

        else:
            log.warning(f"Unknown operation '{operation}' on '{fname}' — skipping.")

    log.info(f"Patch summary: {len(applied)} applied, {len(operations) - len(applied)} skipped.")
    # Expose created files so callers can clean them up on rollback
    apply_patch_operations._last_created = created
    return bool(applied)
