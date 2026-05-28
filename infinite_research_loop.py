"""Continuous evolution loop with execution-grounded validation.

This is the primary entry point for the Grounded Evolution system.
Unlike the lexical-only loop (auto_evolve.py), this loop:
1. Generates actual code from prompts via LLM
2. Validates generated code by running it (AST, pytest, flake8)
3. Scores prompts based on real execution outcomes
4. Runs indefinitely with auto-commit on improvement

This is what makes the evolution "grounded" — fitness is determined
by real code quality, not just keyword matching.
"""

import json
import os
import random
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

from generator import generate_code, write_project_files
from mutation_engine import mutate_prompt, crossover_prompts
from population_manager import (
    load_population,
    save_population,
    select_best,
    select_tournament,
    add_individual,
)
from evaluator.runtime_evaluator import evaluate_project

OUTPUT_DIR: Path = Path("generated_projects")
BENCHMARKS_FILE: Path = Path("benchmarks/tasks.json")
RUNTIME_LOGS: Path = Path("runtime_logs")

Benchmark = dict[str, str]
Metrics = dict[str, Any]


def load_benchmarks() -> list[Benchmark]:
    """Load benchmark task definitions from JSON."""
    if BENCHMARKS_FILE.exists():
        with open(BENCHMARKS_FILE) as f:
            return json.load(f)
    return [{"name": "default", "prompt": "Generate a clean Python project"}]


def git_auto_commit(message: str) -> None:
    """Auto-commit all changes with the given message."""
    try:
        subprocess.run(["git", "add", "-A"], capture_output=True, timeout=10)
        subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True,
            timeout=10,
        )
    except Exception:
        pass


def run_benchmark(prompt: str, benchmark: Benchmark, cycle_num: int) -> tuple[Metrics, Path, list[str]]:
    """Run a full generation + evaluation cycle for a benchmark."""
    task_dir: Path = OUTPUT_DIR / f"cycle_{cycle_num}_{benchmark['name']}"
    generated: str = generate_code(prompt)
    files: list[str] = write_project_files(task_dir, generated)
    metrics: Metrics = evaluate_project(task_dir)
    return metrics, task_dir, files


def check_keyword_coverage(generated_text: str) -> float:
    """Check basic Python keyword coverage in generated code."""
    keywords: list[str] = [
        "def ", "class ", "import ", "async ", "await ",
        "try:", "except", "return ", "if ", "elif ", "else:",
        "for ", "while ", "with ", "lambda", "yield ",
        "@", "True", "False", "None", "raise ",
    ]
    present: int = sum(1 for kw in keywords if kw in generated_text)
    total: int = len(keywords)
    return round(present / total * 10, 1) if total > 0 else 0


def evaluate_generated_content(metrics: Metrics) -> float:
    """Compute content quality bonus from execution metrics."""
    bonus: float = 0
    if metrics.get("syntax", {}).get("valid"):
        bonus += 5
    node_count: int = metrics.get("ast_nodes", 0)
    if node_count > 50:
        bonus += 3
    elif node_count > 20:
        bonus += 1
    if metrics.get("structure", {}).get("functions", 0) >= 3:
        bonus += 2
    if metrics.get("structure", {}).get("classes", 0) >= 2:
        bonus += 2
    if metrics.get("has_tests"):
        bonus += 3
    if metrics.get("has_readme"):
        bonus += 2
    if metrics.get("has_requirements"):
        bonus += 3
    return bonus


def evolve_cycle(cycle_num: int, generation: int) -> float:
    """Run one evolution cycle: select, mutate, generate, validate, persist."""
    population = load_population()
    benchmarks: list[Benchmark] = load_benchmarks()

    if not population:
        population = load_population()

    best = select_best(population, k=1)
    parent = best[0] if best else population[0]

    if random.random() < 0.3 and len(population) >= 2:
        second = select_tournament(population)
        mutated_prompt: str = crossover_prompts(str(parent["prompt"]), str(second["prompt"]))
    else:
        mutated_prompt = mutate_prompt(str(parent["prompt"]))

    benchmark: Benchmark = random.choice(benchmarks) if random.random() < 0.7 else benchmarks[0]

    metrics, task_dir, files = run_benchmark(mutated_prompt, benchmark, cycle_num)

    base_score: float = float(metrics.get("final_score", 0))
    content_bonus: float = evaluate_generated_content(metrics)
    total_score: float = round(base_score + content_bonus, 1)

    population = add_individual(population, mutated_prompt, total_score, generation)

    log_entry: dict[str, Any] = {
        "cycle": cycle_num,
        "generation": generation,
        "benchmark": benchmark["name"],
        "base_score": base_score,
        "content_bonus": content_bonus,
        "total_score": total_score,
        "files_generated": files,
        "metrics": metrics,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    RUNTIME_LOGS.mkdir(exist_ok=True)
    with open(RUNTIME_LOGS / f"cycle_{cycle_num}.json", "w") as f:
        json.dump(log_entry, f, indent=2)

    save_population(population)

    try:
        subprocess.run(
            [sys.executable, "beautify_readme.py"],
            capture_output=True,
            timeout=10,
        )
    except Exception:
        pass

    summary: str = (
        f"Cycle {cycle_num} | Gen {generation} | "
        f"Benchmark: {benchmark['name']} | "
        f"Score: {total_score} (base={base_score}, bonus={content_bonus}) | "
        f"Files: {len(files)}"
    )
    print(summary)
    return total_score


def main() -> None:
    """Run the infinite evolution loop."""
    print("=" * 60)
    print("GROUNDED EVOLUTION SYSTEM")
    print("=" * 60)
    print("Starting infinite evolution loop...")
    print()

    generation: int = 0
    cycle: int = 0
    best_score: float = 0

    while True:
        try:
            score: float = evolve_cycle(cycle, generation)
            if score > best_score:
                best_score = score
                git_message: str = f"evolution cycle={cycle} gen={generation} score={score}"
                git_auto_commit(git_message)

            generation += 1
            cycle += 1
            time.sleep(10)

        except KeyboardInterrupt:
            print("\nEvolution loop terminated by user.")
            break
        except Exception as e:
            print(f"Error in cycle {cycle}: {e}")
            time.sleep(30)


if __name__ == "__main__":
    main()
