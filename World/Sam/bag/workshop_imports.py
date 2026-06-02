"""
bag/workshop_imports.py — Resolve and import Sam workshop modules by name.
"""

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

_REPAIR_TARGETS = ("sam.py",)


def find_workshop_py(workshop: Path, module_basename: str) -> Path | None:
    """Locate a workshop .py file by stem under workshop_bench/."""
    from bag.workshop_paths import iter_writable_bag_py, relative_posix

    stem = module_basename.removesuffix(".py")
    matches = [f for f in iter_writable_bag_py(workshop) if f.stem == stem]
    if not matches:
        return None
    return sorted(matches, key=lambda p: len(relative_posix(p, workshop)))[0]


def load_callable(workshop: Path, module_basename: str, attr: str, default=None):
    """Import attr from the workshop module named module_basename."""
    path = find_workshop_py(workshop, module_basename)
    if not path:
        if default is not None:
            return default
        raise ImportError(f"No workshop module '{module_basename}' under workshop_bench/")

    mod_name = f"_sam_workshop_{path.stem}_{id(path)}"
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, attr)


def _rel_to_dotted(rel: str) -> str:
    # rel is assumed to start with workshop_bench/
    return Path(rel).with_suffix("").as_posix().replace("/", ".")


def rewrite_import_paths(text: str, path_map: dict[str, str]) -> str:
    """Rewrite from workshop_bench.old.path imports using path_map."""
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


def apply_import_repairs(sam_root: Path, workshop: Path, path_map: dict[str, str], log) -> list[str]:
    """Update import lines in sam.py and all workshop/**/*.py after moves."""
    if not path_map:
        return []

    targets: list[Path] = [sam_root / name for name in _REPAIR_TARGETS if (sam_root / name).exists()]
    for py in sorted(workshop.rglob("*.py")):
        if "rollback_registry" in py.parts or "__pycache__" in py.parts:
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
                rel = f.relative_to(sam_root)
            except ValueError:
                rel = f.name
            log.info(f"Imports updated after workshop move → {rel}")
            repaired.append(str(rel))
    return repaired


def verify_repo_integrity(sam_root: Path, workshop: Path, log) -> bool:
    """Compile-check sam.py and everything under workshop/ and bag/."""
    ok = True
    bag = sam_root / "bag"
    to_check = [sam_root / "sam.py"]
    to_check.extend(p for p in sorted(workshop.rglob("*.py")) if "__pycache__" not in p.parts)
    to_check.extend(p for p in sorted(bag.rglob("*.py")) if "__pycache__" not in p.parts)

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
