"""Surgical patch application shared by Phase V and Phase VI."""

from pathlib import Path

from bag.workshop_paths import FORBIDDEN_BASENAMES, is_allowed_patch_filename, is_allowed_prompt_patch_filename


def apply_patch_operations(operations: list, root: Path, log) -> bool:
    """Apply replace / insert_after / delete ops. Returns True if any succeeded."""
    applied = []
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
            else:
                log.warning(f"Skipping patch on non-existent file '{fname}'.")
            continue

        source = target.read_text(encoding="utf-8")

        if operation == "replace":
            old, new = op.get("old", ""), op.get("new", "")
            if not old:
                log.warning(f"replace on '{fname}': 'old' is empty — skipping.")
                continue
            if old not in source:
                log.warning(f"replace on '{fname}': 'old' string not found — skipping.")
                continue
            target.write_text(source.replace(old, new, 1), encoding="utf-8")
            log.info(f"Applied replace → {fname}")
            applied.append(fname)

        elif operation == "insert_after":
            anchor, new = op.get("anchor", ""), op.get("new", "")
            if not anchor:
                log.warning(f"insert_after on '{fname}': 'anchor' is empty — skipping.")
                continue
            if anchor not in source:
                log.warning(f"insert_after on '{fname}': anchor not found — skipping.")
                continue
            target.write_text(source.replace(anchor, anchor + "\n" + new, 1), encoding="utf-8")
            log.info(f"Applied insert_after → {fname}")
            applied.append(fname)

        elif operation == "delete":
            old = op.get("old", "")
            if not old:
                log.warning(f"delete on '{fname}': 'old' is empty — skipping.")
                continue
            if old not in source:
                log.warning(f"delete on '{fname}': 'old' string not found — skipping.")
                continue
            target.write_text(source.replace(old, "", 1), encoding="utf-8")
            log.info(f"Applied delete → {fname}")
            applied.append(fname)

        else:
            log.warning(f"Unknown operation '{operation}' on '{fname}' — skipping.")

    return bool(applied)


def apply_prompt_patch_operations(operations: list, root: Path, log) -> bool:
    """Same as apply_patch_operations but uses the Phase VI allow-list,
    which additionally permits bag/prompts.py."""
    applied = []
    for op in operations:
        fname = op.get("filename", "")
        operation = op.get("operation", "")

        if not is_allowed_prompt_patch_filename(fname):
            log.warning(f"Blocked prompt patch to '{fname}' — outside allowed scope.")
            continue

        basename = Path(fname).name
        if basename in FORBIDDEN_BASENAMES:
            log.warning(f"Blocked prompt patch to governance file '{fname}'.")
            continue

        if "content" in op:
            log.warning(f"Blocked full-file rewrite on '{fname}' — 'content' key forbidden.")
            continue

        target = root / fname
        if not target.exists():
            log.warning(f"Skipping prompt patch on non-existent file '{fname}'.")
            continue

        source = target.read_text(encoding="utf-8")

        if operation == "replace":
            old, new = op.get("old", ""), op.get("new", "")
            if not old:
                log.warning(f"replace on '{fname}': 'old' is empty — skipping.")
                continue
            if old not in source:
                log.warning(f"replace on '{fname}': 'old' string not found — skipping.")
                continue
            target.write_text(source.replace(old, new, 1), encoding="utf-8")
            log.info(f"Applied prompt patch replace → {fname}")
            applied.append(fname)

        elif operation == "insert_after":
            anchor, new = op.get("anchor", ""), op.get("new", "")
            if not anchor or anchor not in source:
                log.warning(f"insert_after on '{fname}': anchor not found — skipping.")
                continue
            target.write_text(source.replace(anchor, anchor + "\n" + new, 1), encoding="utf-8")
            log.info(f"Applied prompt patch insert_after → {fname}")
            applied.append(fname)

        elif operation == "delete":
            old = op.get("old", "")
            if not old or old not in source:
                log.warning(f"delete on '{fname}': 'old' string not found — skipping.")
                continue
            target.write_text(source.replace(old, "", 1), encoding="utf-8")
            log.info(f"Applied prompt patch delete → {fname}")
            applied.append(fname)

        else:
            log.warning(f"Unknown operation '{operation}' on '{fname}' — skipping.")

    return bool(applied)
