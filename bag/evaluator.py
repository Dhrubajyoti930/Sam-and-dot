import json
import logging
from pathlib import Path

BAG         = Path(__file__).parent.resolve()
EXPERIENCES = BAG / "experiences.json"

log = logging.getLogger("evaluator")


def run_ragas_lite() -> list:
    """
    Fix #7 — real memory quality checks instead of a stub.
    Returns a list of issue strings (empty = all clear).
    """
    if not EXPERIENCES.exists():
        log.info("[Evaluator] experiences.json not found — skipping.")
        return []

    with open(EXPERIENCES) as f:
        data = json.load(f)

    if len(data) < 5:
        log.info(f"[Evaluator] Only {len(data)} experiences — skipping (need 5+).")
        return []

    issues = []

    # 1. Required fields present in every entry
    required_fields = ("cycle", "summary", "key_learnings", "sentiment")
    for i, entry in enumerate(data):
        for field in required_fields:
            if field not in entry:
                issues.append(f"Entry {i} (cycle {entry.get('cycle', '?')}) missing field '{field}'.")

    # 2. Sentiment health — >50% negative is a signal
    sentiments = [e.get("sentiment", "unknown") for e in data]
    negative_count = sentiments.count("negative")
    if negative_count / len(data) > 0.5:
        issues.append(
            f"Sentiment warning: {negative_count}/{len(data)} experiences are negative — "
            "Sam may be in a failure loop."
        )

    # 3. Stagnation check — last 3 summaries identical
    if len(data) >= 3:
        recent_summaries = [e.get("summary", "") for e in data[-3:]]
        if len(set(recent_summaries)) == 1:
            issues.append(
                "Stagnation warning: last 3 experience summaries are identical — "
                "Sam may be repeating the same cycle without growth."
            )

    # 4. Cycle continuity — no large gaps
    cycles = sorted(e.get("cycle", 0) for e in data if isinstance(e.get("cycle"), int))
    for i in range(1, len(cycles)):
        if cycles[i] - cycles[i - 1] > 5:
            issues.append(
                f"Continuity gap: cycles jump from {cycles[i-1]} to {cycles[i]} — "
                "experiences may have been incorrectly pruned."
            )

    # 5. key_learnings not empty
    empty_learnings = [
        e.get("cycle", i)
        for i, e in enumerate(data)
        if not e.get("key_learnings")
    ]
    if empty_learnings:
        issues.append(f"Empty key_learnings in cycles: {empty_learnings}.")

    if issues:
        log.warning(f"[Evaluator] {len(issues)} issue(s) found:")
        for issue in issues:
            log.warning(f"  - {issue}")
    else:
        log.info(f"[Evaluator] Memory integrity check passed — {len(data)} experiences, quality OK.")

    return issues


if __name__ == "__main__":
    run_ragas_lite()
