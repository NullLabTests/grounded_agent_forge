#!/usr/bin/env python3
"""Generate human-readable experiment summary tables from run logs.

Usage:
    python analysis/table_report.py                          # From main log
    python analysis/table_report.py --ablation               # From ablation runs
    python analysis/table_report.py --compare                # Compare across conditions
"""

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_main_log() -> list[dict[str, Any]]:
    path = Path("experiments/run_log.jsonl")
    if not path.exists():
        print("No experiment log found at experiments/run_log.jsonl")
        sys.exit(1)
    return [json.loads(line) for line in path.read_text().strip().splitlines() if line]


def load_ablation_runs() -> dict[str, list[dict[str, Any]]]:
    runs_dir = Path("experiments/ablation_runs")
    if not runs_dir.exists():
        print("No ablation runs found at experiments/ablation_runs/")
        sys.exit(1)
    results: dict[str, list[dict[str, Any]]] = {}
    for fpath in sorted(runs_dir.glob("*.jsonl")):
        results[fpath.stem] = [
            json.loads(line) for line in fpath.read_text().strip().splitlines() if line
        ]
    return results


def print_table(title: str, headers: list[str], rows: list[list[str]]) -> None:
    """Print a formatted ASCII table."""
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    sep = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"

    print(f"\n{title}")
    print(sep)
    header_row = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"
    print(header_row)
    print(sep)
    for row in rows:
        print("| " + " | ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(row)) + " |")
    print(sep)


def main_log_report(records: list[dict[str, Any]]) -> None:
    """Print summary table from main experiment log."""
    print(f"Main log: {len(records)} cycles across {len(set(r.get('benchmark', '?') for r in records))} benchmarks")

    # Per-benchmark stats
    bench_stats: dict[str, dict[str, float]] = {}
    for r in records:
        b = r.get("benchmark", "?")
        if b not in bench_stats:
            bench_stats[b] = {"count": 0, "scores": [], "best_score": 0, "total_tokens": 0}
        bench_stats[b]["count"] += 1
        bench_stats[b]["scores"].append(r.get("score", 0))
        bench_stats[b]["best_score"] = max(bench_stats[b]["best_score"], r.get("score", 0))
        bench_stats[b]["total_tokens"] += r.get("llm_total_tokens", 0)

    headers = ["Benchmark", "Cycles", "Best", "Avg", "Latest", "Total Tokens"]
    rows: list[list[str]] = []
    for b, s in sorted(bench_stats.items()):
        scores = s["scores"]
        rows.append([
            b,
            str(s["count"]),
            f'{s["best_score"]:.1f}',
            f'{sum(scores) / len(scores):.1f}',
            f'{scores[-1]:.1f}',
            f'{s["total_tokens"]:,}',
        ])
    print_table("Benchmark Summary", headers, rows)

    # Recent cycles
    recent = records[-20:]
    headers2 = ["Cycle", "Benchmark", "Score", "Mutation", "Tokens", "Duration"]
    rows2: list[list[str]] = []
    for r in recent:
        rows2.append([
            str(r.get("cycle", "?")),
            str(r.get("benchmark", "?")),
            f'{r.get("score", 0):.1f}',
            str(r.get("mutation", "?")),
            str(r.get("llm_total_tokens", 0)),
            f'{r.get("cycle_duration_s", 0):.1f}s',
        ])
    print_table("Last 20 Cycles", headers2, rows2)


def ablation_report(conditions: dict[str, list[dict[str, Any]]]) -> None:
    """Print summary table per ablation condition."""
    print(f"Ablation runs: {len(conditions)} condition files")

    # Parse condition name and benchmark from file stem
    parsed: dict[str, dict[str, Any]] = {}
    for cid, records in conditions.items():
        # cid is like "full_cli_task_manager"
        parts = cid.rsplit("_", 2)
        if len(parts) >= 3:
            cond_name = parts[0]
            bench_name = "_".join(parts[1:])
        else:
            cond_name = cid
            bench_name = "?"

        key = f"{cond_name} / {bench_name}"
        scores = [r.get("score", 0) for r in records]
        parsed[key] = {
            "condition": cond_name,
            "benchmark": bench_name,
            "cycles": len(records),
            "best": max(scores) if scores else 0,
            "avg": sum(scores) / len(scores) if scores else 0,
            "final": scores[-1] if scores else 0,
        }

    headers = ["Condition / Benchmark", "Cycles", "Best", "Avg", "Final"]
    rows: list[list[str]] = []
    for key in sorted(parsed):
        p = parsed[key]
        rows.append([
            key,
            str(p["cycles"]),
            f'{p["best"]:.1f}',
            f'{p["avg"]:.1f}',
            f'{p["final"]:.1f}',
        ])
    print_table("Ablation Results", headers, rows)

    # Aggregate by condition
    cond_agg: dict[str, list[float]] = defaultdict(list)
    for key, p in parsed.items():
        cond = p["condition"]
        cond_agg[cond].append(p["best"])

    headers2 = ["Condition", "Benchmarks", "Avg Best", "Max Best"]
    rows2: list[list[str]] = []
    for cond in sorted(cond_agg):
        bests = cond_agg[cond]
        rows2.append([
            cond,
            str(len(bests)),
            f'{sum(bests) / len(bests):.1f}',
            f'{max(bests):.1f}',
        ])
    print_table("Aggregate by Condition", headers2, rows2)


def compare_conditions(conditions: dict[str, list[dict[str, Any]]]) -> None:
    """Side-by-side comparison of all conditions on the same benchmark."""
    # Group by benchmark
    by_benchmark: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for cid, records in conditions.items():
        parts = cid.rsplit("_", 2)
        cond_name = parts[0] if len(parts) >= 3 else cid
        bench_name = "_".join(parts[1:]) if len(parts) >= 3 else "?"
        scores = [r.get("score", 0) for r in records]
        by_benchmark[bench_name][cond_name] = scores

    for bench, conds in sorted(by_benchmark.items()):
        print(f"\nBenchmark: {bench}")
        headers = ["Condition", "Cycles", "Best", "Avg", "Final"]
        rows: list[list[str]] = []
        for cond in sorted(conds):
            scores = conds[cond]
            rows.append([
                cond,
                str(len(scores)),
                f'{max(scores):.1f}',
                f'{sum(scores) / len(scores):.1f}',
                f'{scores[-1]:.1f}',
            ])
        print_table("", headers, rows)


def main() -> None:
    use_ablation = "--ablation" in sys.argv
    use_compare = "--compare" in sys.argv

    if use_ablation or use_compare:
        conditions = load_ablation_runs()
        print(f"\n{'='*60}")
        print("EXPERIMENT REPORT")
        print(f"{'='*60}")
        if use_compare:
            compare_conditions(conditions)
        else:
            ablation_report(conditions)
    else:
        records = load_main_log()
        print(f"\n{'='*60}")
        print("EXPERIMENT REPORT")
        print(f"{'='*60}")
        main_log_report(records)


if __name__ == "__main__":
    main()
