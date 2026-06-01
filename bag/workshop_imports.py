"""
bag/workshop_imports.py — Resolve and import Sam workshop modules by name (any folder).

Core agents (sam.py, dot.py) must not hardcode bag/<folder>/module paths so Sam can
move workshop files without breaking the repo.
"""

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

_REPAIR_TARGETS = ("sam.py",)


def find_workshop_py(bag: Path, module_basename: str) -> Path | None:
    """Locate a workshop .py file by stem (e.g. governance_shield)."""
    from bag.workshop_paths import iter_writable_bag_py, relative_bag_posix

    stem = module_basename.removesuffix(".py")
    matches = [f for f in iter_writable_bag_py(bag) if f.stem == stem]
    if not matches:
        return None
    return sorted(matches, key=lambda p: len(relative_bag_posix(p, bag)))[0]


def load_callable(bag: Path, module_basename: str, attr: str, default=None):
    """Import attr from the workshop module named module_basename (any bag/ subfolder)."""
    path = find_workshop_py(bag, module_basename)
    if not path:
        if default is not None:
            return default
        raise ImportError(f"No workshop module '{module_basename}' under bag/")

    mod_name = f"_sam_workshop_{path.stem}_{id(path)}"
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, attr)


def _rel_to_dotted(rel: str) -> str:
    return "bag." + Path(rel).with_suffix("").as_posix().replace("/", ".")


def rewrite_import_paths(text: str, path_map: dict[str, str]) -> str:
    """Rewrite from bag.old.path imports using path_map (bag-relative posix paths)."""
    out = text
    for old_rel, new_rel in sorted(path_map.items(), key=lambda x: -len(x[0])):
        old_mod = _rel_to_dotted(old_rel)
        new_mod = _rel_to_dotted(new_rel)
        out = re.sub(
            rf"\bfrom\s+{re.escape(old_mod)}\s+import",
            f"from {new_mod} import",
            out,
        )
        out = re.sub(
            rf"\bimport\s+{re.escape(old_mod)}\b",
            f"import {new_mod}",
            out,
        )
    return out


def apply_import_repairs(root: Path, bag: Path, path_map: dict[str, str], log) -> list[str]:
    """Update import lines in sam.py and all bag/**/*.py after workshop moves."""
    if not path_map:
        return []

    targets: list[Path] = [root / name for name in _REPAIR_TARGETS if (root / name).exists()]
    for py in sorted(bag.rglob("*.py")):
        if "rollback_registry" in py.parts:
            continue
        if py not in targets:
            targets.append(py)

    repaired = []
    for f in targets:
        try:
            src = f.read_text(encoding="utf-8")
        except OSError:
            continue
        new_src = rewrite_import_paths(src, path_map)
        if new_src != src:
            f.write_text(new_src, encoding="utf-8")
            try:
                rel = f.relative_to(root)
            except ValueError:
                rel = f.name
            log.info(f"Imports updated after workshop move → {rel}")
            repaired.append(str(rel))
    return repaired


def verify_repo_integrity(root: Path, bag: Path, log) -> bool:
    """Compile-check sam.py, dot.py, and every bag/**/*.py (excl. rollback_registry)."""
    ok = True
    to_check = [root / "sam.py", bag / "dot.py"]
    to_check.extend(
        p for p in sorted(bag.rglob("*.py"))
        if "rollback_registry" not in p.parts
    )
    for f in to_check:
        if not f.exists():
            continue
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(f)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            log.error(f"Compile failed after workshop move: {f.name} — {result.stderr.strip()}")
            ok = False
    return ok

