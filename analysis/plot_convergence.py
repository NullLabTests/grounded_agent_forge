#!/usr/bin/env python3
"""Plot grounded evolution convergence curves from experiment data.

Usage:
    python analysis/plot_convergence.py                          # Use main run_log.jsonl
    python analysis/plot_convergence.py --ablation               # Use per-condition files
    python analysis/plot_convergence.py --ablation --rolling 5   # Rolling average

Output: PNG files in analysis/charts/
"""

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


CHARTS_DIR: Path = Path("analysis/charts")
ROLLING_WINDOW: int = 10  # default rolling average window


def load_main_log() -> list[dict[str, Any]]:
    """Load all cycles from the main experiment log."""
    log_path: Path = Path("experiments/run_log.jsonl")
    if not log_path.exists():
        print("No experiment log found at experiments/run_log.jsonl")
        sys.exit(1)
    return [json.loads(line) for line in log_path.read_text().strip().splitlines() if line]


def load_ablation_runs() -> dict[str, list[dict[str, Any]]]:
    """Load per-condition results from experiments/ablation_runs/*.jsonl."""
    runs_dir: Path = Path("experiments/ablation_runs")
    if not runs_dir.exists():
        print("No ablation runs found at experiments/ablation_runs/")
        sys.exit(1)

    results: dict[str, list[dict[str, Any]]] = {}
    for fpath in sorted(runs_dir.glob("*.jsonl")):
        condition: str = fpath.stem
        results[condition] = [
            json.loads(line) for line in fpath.read_text().strip().splitlines() if line
        ]
    return results


def rolling_average(values: list[float], window: int) -> list[float]:
    """Compute rolling average with the given window size."""
    if not values or window <= 1:
        return list(values)
    smoothed: list[float] = []
    for i in range(len(values)):
        start: int = max(0, i - window + 1)
        chunk: list[float] = values[start:i + 1]
        smoothed.append(sum(chunk) / len(chunk))
    return smoothed


def plot_main_convergence(records: list[dict[str, Any]]) -> None:
    """Plot overall score vs cycles from the main log."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed. Install it with: pip install matplotlib")
        return

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    scores: list[float] = [r.get("score", 0) for r in records]
    best: list[float] = []
    best_sofar: float = 0
    for s in scores:
        best_sofar = max(best_sofar, s)
        best.append(best_sofar)

    fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    ax1, ax2 = axes

    # Top: per-cycle score
    ax1.plot(scores, alpha=0.4, color="blue", linewidth=0.8, label="Per-cycle score")
    smoothed = rolling_average(scores, ROLLING_WINDOW)
    ax1.plot(smoothed, color="blue", linewidth=2, label=f"Rolling avg (w={ROLLING_WINDOW})")
    ax1.set_ylabel("Execution Score")
    ax1.set_title("Grounded Evolution: Per-Cycle Scores")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Bottom: best-so-far
    ax2.plot(best, color="green", linewidth=2, label="Best so far")
    ax2.set_xlabel("Cycle")
    ax2.set_ylabel("Best Score")
    ax2.set_title("Grounded Evolution: Best Score Convergence")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    out: Path = CHARTS_DIR / "convergence_main.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved {out}")


def plot_ablation_convergence(conditions: dict[str, list[dict[str, Any]]]) -> None:
    """Plot ablation study comparison: one line per condition."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed. Install it with: pip install matplotlib")
        return

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(2, 1, figsize=(14, 12))

    ax1, ax2 = axes

    colors: dict[str, str] = {
        "full": "blue",
        "mutation_only": "orange",
        "crossover_only": "green",
        "random_walk": "red",
    }
    markers: dict[str, str] = {
        "full": "o",
        "mutation_only": "s",
        "crossover_only": "^",
        "random_walk": "v",
    }

    # Top: per-condition best-so-far
    for cid, records in sorted(conditions.items()):
        scores: list[float] = [r.get("score", 0) for r in records]
        best: list[float] = []
        best_sofar: float = 0
        for s in scores:
            best_sofar = max(best_sofar, s)
            best.append(best_sofar)

        base_cid: str = cid.rsplit("_", 1)[0] if "_" in cid else cid
        color: str = colors.get(base_cid, "gray")
        marker: str = markers.get(base_cid, ".")
        label: str = cid
        ax1.plot(best, color=color, linewidth=1.5, label=label, marker=marker, markevery=max(1, len(best) // 10))

    ax1.set_ylabel("Best Score")
    ax1.set_title("Ablation Study: Best Score Convergence by Condition")
    ax1.legend(fontsize=8, ncol=2)
    ax1.grid(True, alpha=0.3)

    # Bottom: aggregated per-condition (group by condition, average across benchmarks)
    condition_scores: dict[str, list[list[float]]] = defaultdict(list)
    for cid, records in sorted(conditions.items()):
        base_cid = cid.rsplit("_", 1)[0] if "_" in cid else cid
        condition_scores[base_cid].append([r.get("score", 0) for r in records])

    for cond, all_scores in sorted(condition_scores.items()):
        # Average across benchmarks at each cycle
        min_len: int = min(len(s) for s in all_scores)
        avg_scores: list[float] = [sum(s[i] for s in all_scores) / len(all_scores) for i in range(min_len)]
        best_avg: list[float] = []
        best_sofar = 0
        for s in avg_scores:
            best_sofar = max(best_sofar, s)
            best_avg.append(best_sofar)

        color: str = colors.get(cond, "gray")
        marker: str = markers.get(cond, ".")
        ax2.plot(best_avg, color=color, linewidth=2.5, label=cond, marker=marker, markevery=max(1, min_len // 8))

    ax2.set_xlabel("Cycle")
    ax2.set_ylabel("Best Score (avg across benchmarks)")
    ax2.set_title("Ablation Study: Aggregate Convergence (averaged across benchmarks)")
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    out: Path = CHARTS_DIR / "convergence_ablation.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved {out}")


def main() -> None:
    """Main entry point."""
    use_ablation: bool = "--ablation" in sys.argv
    rolling_window: int = ROLLING_WINDOW
    for arg in sys.argv:
        if arg.startswith("--rolling="):
            rolling_window = int(arg.split("=")[1])

    global ROLLING_WINDOW
    ROLLING_WINDOW = rolling_window

    if use_ablation:
        conditions = load_ablation_runs()
        print(f"Loaded {len(conditions)} condition files from experiments/ablation_runs/")
        print(f"Conditions: {', '.join(sorted(conditions.keys()))}")
        plot_ablation_convergence(conditions)
    else:
        records = load_main_log()
        n_benchmarks = len(set(r.get("benchmark", "?") for r in records))
        print(f"Loaded {len(records)} cycles across {n_benchmarks} benchmarks")
        plot_main_convergence(records)

    print(f"Charts saved to {CHARTS_DIR}/")


if __name__ == "__main__":
    main()
