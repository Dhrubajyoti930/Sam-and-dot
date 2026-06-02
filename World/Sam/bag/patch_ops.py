"""Surgical patch application shared by Phase V and Phase VI."""

import ast
import re
from pathlib import Path

from bag.workshop_paths import FORBIDDEN_BASENAMES, is_allowed_patch_filename


def inject_missing_imports(code: str) -> str:
    """Detects common missing stdlib imports and injects them if used."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return code

    defined = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Param)):
            defined.add(node.id)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                defined.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                defined.add(alias.asname or alias.name)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            defined.add(node.name)

    missing = []

    # Use AST for more precise usage detection
    used_modules = {
        node.value.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
    }

    if "re" not in defined and "re" in used_modules:
        missing.append("import re")
    if "json" not in defined and "json" in used_modules:
        missing.append("import json")
    if "os" not in defined and "os" in used_modules:
        missing.append("import os")
    if "sys" not in defined and "sys" in used_modules:
        missing.append("import sys")
    if "time" not in defined and "time" in used_modules:
        missing.append("import time")
    if "datetime" not in defined and "datetime" in used_modules:
        missing.append("import datetime")

    if not missing:
        return code

    return "\n".join(missing) + "\n\n" + code


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
                target.write_text(inject_missing_imports(op.get("new", "")), encoding="utf-8")
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

            new_source = source.replace(old, new, 1)
            # Only inject imports into new files. For existing files, write without injection.
            target.write_text(new_source, encoding="utf-8")
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

            new_source = source.replace(anchor, anchor + "\n" + new, 1)
            target.write_text(new_source, encoding="utf-8")
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

    log.info(f"Patch summary: {len(applied)} applied, {len(operations) - len(applied)} skipped.")
    return bool(applied)
