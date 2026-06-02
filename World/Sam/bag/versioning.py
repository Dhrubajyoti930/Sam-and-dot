import subprocess
import re


def get_next_version(current_version="0.0.0"):
    """Calculate next SemVer based on git log.
    Fix #9 -- limit to last 100 commits to avoid unbounded memory use.
    """
    try:
        log = subprocess.check_output(
            ["git", "log", "--max-count=100", "--pretty=%s"]  # Fix #9
        ).decode()
    except subprocess.CalledProcessError:
        return current_version

    major, minor, patch = map(int, current_version.split("."))

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
