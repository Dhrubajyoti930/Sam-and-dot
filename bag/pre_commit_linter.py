import re
import json
from pathlib import Path

def lint_commit_message(message: str, lint_mode: str = "warning"):
    """Validates message against Conventional Commits: <type>(<scope>): <subject>"""
    pattern = r"^(feat|fix|docs|style|refactor|perf|test|chore)(\(.+\))?: .{1,}"
    is_valid = bool(re.match(pattern, message))
    
    if not is_valid and lint_mode == "strict":
        raise ValueError(f"Commit message failed linting: {message}")
    return is_valid

if __name__ == "__main__":
    assert lint_commit_message("feat(sam): add linter") == True
    assert lint_commit_message("fix: typo") == False
    assert lint_commit_message("chore(test): bad format") == True