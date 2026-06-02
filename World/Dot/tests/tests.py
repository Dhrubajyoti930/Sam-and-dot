"""
World/Dot/tests/tests.py -- Behavioural Test Suite for Sam-and-dot
"""

import sys
import ast
from pathlib import Path

# Path resolving for World structure
TESTS_DIR = Path(__file__).parent.resolve()
DOT_DIR   = TESTS_DIR.parent.resolve()
ROOT      = DOT_DIR.parent.resolve() # World/
SAM_DIR   = ROOT / "Sam"

FAILURES = []

def check(condition: bool, message: str):
    if not condition:
        FAILURES.append(message)


# ===============================================================================
# SECTION 1 -- Governance: World structure integrity
# ===============================================================================

check((ROOT / "mail").exists(), "FAIL: World/mail/ is missing.")
check((ROOT / "mail" / "dot_to_sam").exists(), "FAIL: World/mail/dot_to_sam/ is missing.")
check((ROOT / "mail" / "sam_to_dot").exists(), "FAIL: World/mail/sam_to_dot/ is missing.")

check((SAM_DIR / "sam.py").exists(), "FAIL: World/Sam/sam.py is missing.")
check((DOT_DIR / "dot.py").exists(), "FAIL: World/Dot/dot.py is missing.")

check((SAM_DIR / "bag" / "wisdom.txt").exists(), "FAIL: Sam's wisdom.txt is missing.")
check((DOT_DIR / "bag" / "wisdom.txt").exists(), "FAIL: Dot's wisdom.txt is missing.")
check((SAM_DIR / "bag" / "SAM_PERSONALITY.md").exists(), "FAIL: SAM_PERSONALITY.md is missing.")

check((SAM_DIR / "My_memories" / "goals.json").exists(), "FAIL: goals.json is missing.")
check((SAM_DIR / "My_memories" / "experiences.json").exists(), "FAIL: experiences.json is missing.")


# ===============================================================================
# SECTION 2 -- sam.py structural integrity
# ===============================================================================

sam_src = (SAM_DIR / "sam.py").read_text(encoding="utf-8")

check("def self_check()" in sam_src, "FAIL: self_check() missing from sam.py.")
check("def _rollback()" in sam_src, "FAIL: _rollback() missing.")
check("read_motion()" in sam_src, "FAIL: read_motion() missing.")
check("MAIL_IN" in sam_src, "FAIL: MAIL_IN constant missing in sam.py.")

# Verify sam.py is valid Python
try:
    ast.parse(sam_src)
except SyntaxError as e:
    check(False, f"FAIL: sam.py has a syntax error: {e}")


# ===============================================================================
# SECTION 3 -- dot.py structural integrity
# ===============================================================================

dot_src = (DOT_DIR / "dot.py").read_text(encoding="utf-8")

check("MAIL_OUT" in dot_src, "FAIL: MAIL_OUT constant missing in dot.py.")
check("def wisdom_check()" in dot_src, "FAIL: wisdom_check() missing in dot.py.")

try:
    ast.parse(dot_src)
except SyntaxError as e:
    check(False, f"FAIL: dot.py has a syntax error: {e}")


# ===============================================================================
# SECTION 4 -- infra package checks
# ===============================================================================

sam_bag = SAM_DIR / "bag"
check((sam_bag / "workshop.py").exists(), "FAIL: workshop.py missing from Sam's bag.")
check((sam_bag / "workshop_paths.py").exists(), "FAIL: workshop_paths.py missing.")
check((sam_bag / "workshop_imports.py").exists(), "FAIL: workshop_imports.py missing.")
check((sam_bag / "bag_paths.py").exists(), "FAIL: bag_paths.py missing.")

# Check all .py in Sam's bag
for f in sam_bag.glob("*.py"):
    try:
        ast.parse(f.read_text(encoding="utf-8"))
    except SyntaxError as e:
        check(False, f"FAIL: Syntax error in {f.name}: {e}")

check((sam_bag / "api_resilience.py").exists(), "FAIL: api_resilience.py missing from Sam's bag.")
check((sam_bag / "metrics.py").exists(), "FAIL: metrics.py missing from Sam's bag.")

# Section 5: Dot's bag infrastructure check
dot_bag = DOT_DIR / "bag"
for f in dot_bag.glob("*.py"):
    try:
        ast.parse(f.read_text(encoding="utf-8"))
    except SyntaxError as e:
        check(False, f"FAIL: Syntax error in Dot's {f.name}: {e}")


# ===============================================================================
# REPORT
# ===============================================================================

if FAILURES:
    print(f"\n{'='*60}")
    print(f"WORLD BEHAVIOUR CHECK FAILED -- {len(FAILURES)} issue(s) found:")
    print('='*60)
    for i, f in enumerate(FAILURES, 1):
        print(f"  {i}. {f}")
    print('='*60)
    sys.exit(1)
else:
    print("World behaviour check passed -- 100% stable.")
    sys.exit(0)
