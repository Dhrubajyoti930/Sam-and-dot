import subprocess
import re

def get_next_version(current_version="0.0.0"):
    """Calculate next SemVer based on git log."""
    log = subprocess.check_output(["git", "log", "--pretty=%s"]).decode()
    major, minor, patch = map(int, current_version.split('.'))
    
    if "BREAKING CHANGE" in log or re.search(r"^\w+(\(.*\))?!:", log):
        return f"{major + 1}.0.0"
    if re.search(r"^feat(\(.*\))?:", log, re.M):
        return f"{major}.{minor + 1}.0"
    if re.search(r"^fix(\(.*\))?:", log, re.M):
        return f"{major}.{minor}.{patch + 1}"
    return current_version

def check_commit(message):
    pattern = r"^(feat|fix|docs|style|refactor|perf|test|chore)(\(.+\))?: .{1,}"
    return bool(re.match(pattern, message))