#!/usr/bin/env python3
"""Orchestrate ablation experiments across benchmarks.

Usage:
    python run_experiment.py                          # Run full experiment grid
    python run_experiment.py --quick                  # 10 cycles per condition for smoke test
    python run_experiment.py --resume                 # Skip completed conditions
    python run_experiment.py --list                   # Show conditions and exit

Design:
    Each (condition × benchmark) pair gets its own population snapshot and
    results file. This prevents interference between conditions and allows
    clean comparisons.

Conditions:
    full             mutation=True,  crossover=True   (baseline)
    mutation_only    mutation=True,  crossover=False
    crossover_only   mutation=False, crossover=True
    random_walk      mutation=False, crossover=False  (no-op baseline)
"""

import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any


CYCLES_DEFAULT: int = 100
POPULATION_BACKUP: Path = Path("population/population.json.bak")
EXPERIMENTS_DIR: Path = Path("experiments/ablation_runs")
POPULATION_DIR: Path = Path("population")
POPULATION_FILE: Path = Path("population/population.json")
EXPERIMENT_LOG: Path = Path("experiments/run_log.jsonl")


ABLATION_CONDITIONS: list[dict[str, Any]] = [
    {"name": "full", "mutation": True, "crossover": True, "mutation_rate": 0.7},
    {"name": "mutation_only", "mutation": True, "crossover": False, "mutation_rate": 1.0},
    {"name": "crossover_only", "mutation": False, "crossover": True, "mutation_rate": 0.0},
    {"name": "random_walk", "mutation": False, "crossover": False, "mutation_rate": 0.0},
]


def get_benchmarks() -> list[dict[str, Any]]:
    """Load benchmarks from tasks.json."""
    from infinite_research_loop import load_benchmarks
    return load_benchmarks()


def condition_id(condition: dict[str, Any], benchmark: dict[str, Any]) -> str:
    return f"{condition['name']}_{benchmark['name']}"


def abort_if_no_api_key() -> None:
    """Exit early if LLM_API_KEY is not set."""
    if not os.environ.get("LLM_API_KEY"):
        print("ERROR: LLM_API_KEY environment variable is required.")
        print("Export it or set it in your .env file.")
        sys.exit(1)


def seed_population() -> None:
    """Seed a fresh population with a single default individual."""
    from population_manager import save_population
    save_population([
        {
            "prompt": "Generate clean production-grade Python software with modular structure, type hints, and comprehensive tests",
            "score": 0,
            "generation": 0,
        }
    ])


def run_condition(
    condition: dict[str, Any],
    benchmark: dict[str, Any],
    cycles: int,
) -> None:
    """Run N evolution cycles for one condition×benchmark pair.

    Results are logged to experiments/run_log.jsonl (with ablation_* fields
    for filtering) and also saved to experiments/ablation_runs/*.jsonl.
    """
    cid: str = condition_id(condition, benchmark)
    tag: str = f"[{cid}]"
    results_file: Path = EXPERIMENTS_DIR / f"{cid}.jsonl"
    results_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"{tag} Starting — {cycles} cycles")
    print(f"{'='*60}")

    # Seed fresh population
    seed_population()

    ablation_config: dict[str, Any] = {
        "mutation": condition["mutation"],
        "crossover": condition["crossover"],
        "mutation_rate": condition["mutation_rate"],
        "signal_hunt": False,
    }

    from infinite_research_loop import evolve_cycle

    start_time: float = time.time()
    scores: list[float] = []

    for i in range(cycles):
        cycle_start: float = time.time()

        score = evolve_cycle(
            cycle_num=i,
            generation=i,
            ablation_override=ablation_config,
            benchmark_name=str(benchmark["name"]),
        )
        scores.append(score)

        cycle_elapsed: float = time.time() - cycle_start
        elapsed: float = time.time() - start_time
        avg_cycle: float = elapsed / (i + 1)
        remaining: float = avg_cycle * (cycles - i - 1)
        best_sofar: float = max(scores)

        # Also write per-condition result file for easy access
        entry: dict[str, Any] = {
            "cycle": i,
            "condition": condition["name"],
            "benchmark": benchmark["name"],
            "score": score,
            "best": best_sofar,
            "elapsed": round(elapsed, 1),
            "avg_cycle_s": round(avg_cycle, 1),
            "estimated_remaining_s": round(remaining, 1),
        }
        with open(results_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

        print(f"  {tag} [{i+1}/{cycles}] score={score:.1f} best={best_sofar:.1f} "
              f"elapsed={elapsed:.0f}s est_remaining={remaining:.0f}s")

    total_elapsed: float = time.time() - start_time
    best_score: float = max(scores)
    final_score: float = scores[-1] if scores else 0
    print(f"\n{tag} DONE — {cycles} cycles in {total_elapsed:.0f}s")
    print(f"  Best: {best_score}  Final: {final_score}")


def list_conditions() -> None:
    """Print the experiment grid without running anything."""
    benchmarks = get_benchmarks()
    print(f"Experiment Grid: {len(ABLATION_CONDITIONS)} conditions × {len(benchmarks)} benchmarks")
    print()
    for cond in ABLATION_CONDITIONS:
        for bench in benchmarks:
            cid = condition_id(cond, bench)
            mut = "✓" if cond["mutation"] else "✗"
            xov = "✓" if cond["crossover"] else "✗"
            rate = cond["mutation_rate"]
            print(f"  {cid:<35} mut={mut} crossover={xov} rate={rate}")
    print()
    print(f"Total runs: {len(ABLATION_CONDITIONS) * len(benchmarks)}")
    print(f"Total cycles: {len(ABLATION_CONDITIONS) * len(benchmarks) * CYCLES_DEFAULT}")


def main() -> None:
    """Main entry point for experiment runner."""
    import argparse

    parser = argparse.ArgumentParser(description="Run ablation experiments")
    parser.add_argument("--quick", action="store_true", help="Run 10 cycles per condition (smoke test)")
    parser.add_argument("--resume", action="store_true", help="Skip already-completed conditions")
    parser.add_argument("--list", action="store_true", help="Show experiment grid and exit")
    parser.add_argument("--cycles", type=int, default=0, help="Override cycles per condition")
    args = parser.parse_args()

    if args.list:
        list_conditions()
        return

    abort_if_no_api_key()

    cycles: int = args.cycles or (10 if args.quick else CYCLES_DEFAULT)
    benchmarks = get_benchmarks()

    print(f"Experiment Runner")
    print(f"  Conditions: {len(ABLATION_CONDITIONS)}")
    print(f"  Benchmarks: {len(benchmarks)}")
    print(f"  Cycles/condition: {cycles}")
    print(f"  Total cycles: {len(ABLATION_CONDITIONS) * len(benchmarks) * cycles}")
    print()

    for condition in ABLATION_CONDITIONS:
        for benchmark in benchmarks:
            cid = condition_id(condition, benchmark)
            results_file: Path = EXPERIMENTS_DIR / f"{cid}.jsonl"

            if args.resume and results_file.exists():
                existing = len(results_file.read_text().strip().splitlines())
                if existing >= cycles:
                    print(f"Skipping {cid} — already has {existing}/{cycles} cycles")
                    continue

            run_condition(condition, benchmark, cycles)

    print(f"\n{'='*60}")
    print("All experiments complete!")
    print(f"{'='*60}")
    print("Results by condition:")
    for condition in ABLATION_CONDITIONS:
        for benchmark in benchmarks:
            cid = condition_id(condition, benchmark)
            rf = EXPERIMENTS_DIR / f"{cid}.jsonl"
            if rf.exists():
                scores = [json.loads(line)["score"] for line in rf.read_text().strip().splitlines() if line]
                best = max(scores) if scores else "N/A"
                final = scores[-1] if scores else "N/A"
                avg = sum(scores) / len(scores) if scores else 0
                print(f"  {cid:<35} best={best} final={final} avg={avg:.1f}")


if __name__ == "__main__":
    main()
