import json
import os
import random
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

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

OUTPUT_DIR = Path("generated_projects")
BENCHMARKS_FILE = Path("benchmarks/tasks.json")
RUNTIME_LOGS = Path("runtime_logs")


def load_benchmarks():
    if BENCHMARKS_FILE.exists():
        with open(BENCHMARKS_FILE) as f:
            return json.load(f)
    return [{"name": "default", "prompt": "Generate a clean Python project"}]


def git_auto_commit(message):
    try:
        subprocess.run(["git", "add", "-A"], capture_output=True, timeout=10)
        subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True,
            timeout=10,
        )
    except Exception:
        pass


def run_benchmark(prompt, benchmark, cycle_num):
    task_dir = OUTPUT_DIR / f"cycle_{cycle_num}_{benchmark['name']}"
    generated = generate_code(prompt)
    files = write_project_files(task_dir, generated)
    metrics = evaluate_project(task_dir)
    return metrics, task_dir, files


def check_keyword_coverage(generated_text):
    coverage = 0
    keywords = [
        "def ", "class ", "import ", "async ", "await ",
        "try:", "except", "return ", "if ", "elif ", "else:",
        "for ", "while ", "with ", "lambda", "yield ",
        "@", "True", "False", "None", "raise ",
    ]
    present = sum(1 for kw in keywords if kw in generated_text)
    total = len(keywords)
    coverage = round(present / total * 10, 1) if total > 0 else 0
    return coverage


def evaluate_generated_content(metrics):
    bonus = 0
    if metrics.get("syntax", {}).get("valid"):
        bonus += 5
    node_count = metrics.get("ast_nodes", 0)
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


def evolve_cycle(cycle_num, generation):
    population = load_population()
    benchmarks = load_benchmarks()

    if not population:
        population = load_population()

    best = select_best(population, k=1)
    parent = best[0] if best else population[0]

    if random.random() < 0.3 and len(population) >= 2:
        second = select_tournament(population)
        mutated_prompt = crossover_prompts(parent["prompt"], second["prompt"])
    else:
        mutated_prompt = mutate_prompt(parent["prompt"])

    benchmark = random.choice(benchmarks) if random.random() < 0.7 else benchmarks[0]

    metrics, task_dir, files = run_benchmark(mutated_prompt, benchmark, cycle_num)

    base_score = metrics.get("final_score", 0)
    content_bonus = evaluate_generated_content(metrics)
    total_score = round(base_score + content_bonus, 1)

    population = add_individual(population, mutated_prompt, total_score, generation)

    log_entry = {
        "cycle": cycle_num,
        "generation": generation,
        "benchmark": benchmark["name"],
        "base_score": base_score,
        "content_bonus": content_bonus,
        "total_score": total_score,
        "files_generated": files,
        "metrics": metrics,
        "timestamp": datetime.utcnow().isoformat(),
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

    summary = (
        f"Cycle {cycle_num} | Gen {generation} | "
        f"Benchmark: {benchmark['name']} | "
        f"Score: {total_score} (base={base_score}, bonus={content_bonus}) | "
        f"Files: {len(files)}"
    )
    print(summary)
    return total_score


def main():
    print("=" * 60)
    print("GROUNDED EVOLUTION SYSTEM")
    print("=" * 60)
    print("Starting infinite evolution loop...")
    print()

    generation = 0
    cycle = 0
    best_score = 0

    while True:
        try:
            score = evolve_cycle(cycle, generation)
            if score > best_score:
                best_score = score
                git_message = f"evolution cycle={cycle} gen={generation} score={score}"
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
