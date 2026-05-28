"""Regression tracking and trend analysis for evolution cycles.

Persists cycle outcomes and provides trend detection to monitor
whether the system is improving, stable, or declining over time.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any


HISTORY_FILE: Path = Path("reports/evolution_history.json")

HistoryEntry = dict[str, Any]
History = list[HistoryEntry]
Summary = dict[str, Any]


def load_history() -> History:
    """Load evolution history from JSON file."""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return []


def save_history(history: History) -> None:
    """Persist evolution history to JSON file."""
    HISTORY_FILE.parent.mkdir(exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def log_cycle(
    cycle_num: int,
    generation: int,
    benchmark: str,
    total_score: float,
    base_score: float,
    files_count: int,
) -> History:
    """Record a single evolution cycle outcome."""
    history: History = load_history()
    history.append({
        "cycle": cycle_num,
        "generation": generation,
        "benchmark": benchmark,
        "total_score": total_score,
        "base_score": base_score,
        "files_count": files_count,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    save_history(history)
    return history


def get_trend(history: History | None = None) -> str:
    """Determine the recent trend direction from history."""
    if history is None:
        history = load_history()
    if len(history) < 2:
        return "insufficient_data"
    recent: History = history[-5:] if len(history) >= 5 else history
    scores: list[float] = [float(h["total_score"]) for h in recent]
    if len(scores) >= 3:
        if scores[-1] > scores[0]:
            return "improving"
        elif scores[-1] < scores[0]:
            return "declining"
    return "stable"


def get_summary() -> Summary:
    """Return a summary of all evolution history."""
    history: History = load_history()
    if not history:
        return {"cycles": 0, "best_score": 0, "avg_score": 0, "trend": "no_data"}
    scores: list[float] = [float(h["total_score"]) for h in history]
    return {
        "cycles": len(history),
        "best_score": max(scores),
        "best_cycle": max(history, key=lambda h: float(h["total_score"]))["cycle"],
        "avg_score": round(sum(scores) / len(scores), 1),
        "trend": get_trend(history),
    }
