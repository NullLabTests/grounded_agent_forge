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

from population_manager import PopulationEntry

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

from generator import generate_code, write_project_files
from mutation_engine import mutate_prompt, crossover_prompts, record_mutation_outcome
from population_manager import (
    load_population,
    save_population,
    select_best,
    select_tournament,
    add_individual,
)
from evaluator.runtime_evaluator import evaluate_project

OUTPUT_DIR: Path = Path("generated_projects")
ARCHIVE_DIR: Path = Path("experiments/projects")
BENCHMARKS_FILE: Path = Path("benchmarks/tasks.json")
EXPERIMENT_LOG: Path = Path("experiments/run_log.jsonl")

Benchmark = dict[str, str | dict[str, str]]
Metrics = dict[str, Any]


# === Ablation experiment configuration ===
# Set these before running to control which evolution operators are active.
# Each ablation isolates one variable to measure its contribution.
ABLATION: dict[str, Any] = {
    "mutation": True,       # mutate_prompt on selected parent
    "crossover": True,      # crossover_prompts on two parents
    "mutation_rate": 0.7,   # probability of mutation when both are enabled
    "signal_hunt": True,    # inject missing evaluate.py keywords
}


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


def run_benchmark(prompt: str, benchmark: Benchmark, cycle_num: int) -> tuple[Metrics, Path, list[str], dict[str, Any]]:
    """Run a full generation + evaluation cycle for a benchmark.

    Returns (metrics, task_dir, files, llm_usage).
    """
    task_dir: Path = OUTPUT_DIR / f"cycle_{cycle_num}_{benchmark['name']}"
    generated: str
    usage: dict[str, Any]
    generated, usage = generate_code(prompt)
    files: list[str] = write_project_files(task_dir, generated)
    metrics: Metrics = evaluate_project(task_dir, benchmark)
    return metrics, task_dir, files, usage


def archive_project(task_dir: Path, cycle_num: int, benchmark_name: str, metrics: Metrics, usage: dict[str, Any], prompt: str) -> None:
    """Archive a generated project with full metadata for later review."""
    archive_path: Path = ARCHIVE_DIR / f"{benchmark_name}" / f"cycle_{cycle_num:04d}"
    archive_path.mkdir(parents=True, exist_ok=True)

    for fpath in task_dir.rglob("*"):
        if fpath.is_file():
            rel: str = str(fpath.relative_to(task_dir))
            dest: Path = archive_path / rel
            dest.parent.mkdir(exist_ok=True)
            try:
                dest.write_text(fpath.read_text(errors="replace"))
            except Exception:
                pass

    metadata: dict[str, Any] = {
        "cycle": cycle_num,
        "benchmark": benchmark_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt": prompt,
        "metrics": {k: v for k, v in metrics.items() if k != "prompt"},
        "llm_usage": usage,
    }
    (archive_path / "metadata.json").write_text(json.dumps(metadata, indent=2))


def append_experiment_log(entry: dict[str, Any]) -> None:
    """Append one cycle result to the JSONL experiment log."""
    EXPERIMENT_LOG.parent.mkdir(exist_ok=True)
    with open(EXPERIMENT_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def evolve_cycle(
    cycle_num: int,
    generation: int,
    ablation_override: dict[str, bool] | None = None,
    benchmark_name: str | None = None,
) -> float:
    """Run one evolution cycle: select, mutate, generate, validate, persist.

    ablation_override: overrides the global ABLATION dict for this cycle.
    benchmark_name:      if set, use this specific benchmark instead of random selection.
    Falls back to the global ABLATION dict.
    """
    config: dict[str, Any] = ablation_override if ablation_override is not None else dict(ABLATION)
    population = load_population()
    benchmarks: list[Benchmark] = load_benchmarks()

    if not population:
        return 0.0

    best = select_best(population, k=1)
    parent = best[0] if best else population[0]
    parent_score: float = float(parent.get("score", 0))
    second: PopulationEntry | None = select_tournament(population) if len(population) >= 2 else None

    mutated_prompt: str = str(parent["prompt"])
    applied_mutation: str = "none"
    applied_crossover: str | None = None
    mutation_desc: str = ""

    if config.get("crossover") and second and random.random() > config.get("mutation_rate", 0.7):
        mutated_prompt = crossover_prompts(str(parent["prompt"]), str(second["prompt"]))
        applied_mutation = "crossover"
        applied_crossover = str(second["prompt"])[:80]
    elif config.get("mutation"):
        mutated_prompt, mutation_desc = mutate_prompt(str(parent["prompt"]))
        applied_mutation = "mutation"

    if benchmark_name:
        benchmark_candidates: list[Benchmark] = [b for b in benchmarks if b.get("name") == benchmark_name]
        benchmark = benchmark_candidates[0] if benchmark_candidates else benchmarks[0]
    else:
        benchmark = random.choice(benchmarks)

    cycle_start: float = time.time()
    metrics, task_dir, files, usage = run_benchmark(mutated_prompt, benchmark, cycle_num)
    cycle_duration: float = time.time() - cycle_start

    if not files:
        return 0.0

    base_score: float = float(metrics.get("final_score", 0))
    total_score: float = round(base_score, 1)

    population = add_individual(population, mutated_prompt, total_score, generation)

    archive_project(task_dir, cycle_num, str(benchmark["name"]), metrics, usage, mutated_prompt)

    log_entry: dict[str, Any] = {
        "cycle": cycle_num,
        "generation": generation,
        "benchmark": benchmark["name"],
        "score": total_score,
        "mutation": applied_mutation,
        "crossover_source": applied_crossover,
        "ablation_mutation": config.get("mutation", True),
        "ablation_crossover": config.get("crossover", True),
        "ablation_mutation_rate": config.get("mutation_rate", 0.7),
        "files_generated": len(files),
        "syntax_valid": metrics.get("syntax", {}).get("valid", False),
        "pytest_pass": metrics.get("pytest", {}).get("success", False),
        "hidden_tests_pass": metrics.get("hidden_tests", {}).get("success", False),
        "ast_nodes": metrics.get("ast_nodes", 0),
        "functions": metrics.get("structure", {}).get("functions", 0),
        "classes": metrics.get("structure", {}).get("classes", 0),
        "has_tests": metrics.get("has_tests", False),
        "test_quality": metrics.get("test_quality", 0.0),
        "test_quality_total": metrics.get("test_quality_total", 0.0),
        "has_readme": metrics.get("has_readme", False),
        "has_requirements": metrics.get("has_requirements", False),
        "llm_prompt_tokens": usage.get("prompt_tokens", 0),
        "llm_completion_tokens": usage.get("completion_tokens", 0),
        "llm_total_tokens": usage.get("total_tokens", 0),
        "llm_model": usage.get("model", "unknown"),
        "llm_duration_s": usage.get("duration_seconds", 0),
        "cycle_duration_s": round(cycle_duration, 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    append_experiment_log(log_entry)

    save_population(population)

    try:
        subprocess.run(
            [sys.executable, "beautify_readme.py"],
            capture_output=True,
            timeout=10,
        )
    except Exception:
        pass

    if cycle_num > 0 and cycle_num % 10 == 0:
        try:
            subprocess.run(
                [sys.executable, "reports/summary_report.py"],
                capture_output=True,
                timeout=15,
            )
        except Exception:
            pass

    summary: str = (
        f"Cycle {cycle_num} | Gen {generation} | "
        f"Benchmark: {benchmark['name']} | "
        f"Score: {total_score} | "
        f"Mut: {applied_mutation} | "
        f"Files: {len(files)} | "
        f"Tokens: {usage.get('total_tokens', 0)} | "
        f"Time: {cycle_duration:.1f}s"
    )
    if mutation_desc:
        score_delta: float = total_score - parent_score
        record_mutation_outcome(mutation_desc, score_delta)

    print(summary)
    return total_score


def main() -> None:
    """Run the infinite evolution loop with experiment logging."""
    print("=" * 60)
    print("GROUNDED EVOLUTION SYSTEM")
    print("=" * 60)
    print(f"Mutation: {ABLATION['mutation']}, Crossover: {ABLATION['crossover']}")
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
