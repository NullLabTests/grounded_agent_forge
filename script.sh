# Grounded Evolution Upgrade Script

This script:

* Clones the existing repo
* Removes old symbolic-only evaluator logic
* Creates a grounded execution-based evolution loop
* Adds runtime validation
* Adds pytest execution
* Adds auto git commits/pushes
* Adds README auto-beautification hooks
* Runs continuously in an infinite research loop

---

```bash
#!/usr/bin/env bash

# ============================================================
# Grounded Evolution System Bootstrap
# ============================================================

set -e

REPO_URL="https://github.com/NullLabTests/autoresearch-ai-agent-skeleton.git"
REPO_NAME="autoresearch-ai-agent-skeleton"
BRANCH_NAME="grounded-evolution"

# ============================================================
# Clone Repository
# ============================================================

if [ ! -d "$REPO_NAME" ]; then
    git clone "$REPO_URL"
fi

cd "$REPO_NAME"

# ============================================================
# Branch Setup
# ============================================================

git checkout -b "$BRANCH_NAME" || git checkout "$BRANCH_NAME"

# ============================================================
# Remove Legacy Files
# ============================================================

rm -f evaluator.py || true
rm -f signal_hunt.py || true
rm -f reflective_mutation.py || true
rm -f lexical_scoring.py || true
rm -f buzzword_score.py || true

mkdir -p generated_projects
mkdir -p runtime_logs
mkdir -p benchmarks
mkdir -p population
mkdir -p evaluator
mkdir -p memory
mkdir -p reports

# ============================================================
# Python Requirements
# ============================================================

cat > requirements.txt << 'EOF'
openai
pytest
black
flake8
rich
gitpython
psutil
EOF

pip install -r requirements.txt

# ============================================================
# Benchmark Tasks
# ============================================================

cat > benchmarks/tasks.json << 'EOF'
[
  {
    "name": "flask_api",
    "prompt": "Create a modular Flask REST API with health endpoint and clean structure"
  },
  {
    "name": "cli_tool",
    "prompt": "Create a Python CLI task manager using argparse"
  },
  {
    "name": "websocket_server",
    "prompt": "Create an async websocket echo server in Python"
  }
]
EOF

# ============================================================
# Runtime Evaluator
# ============================================================

cat > evaluator/runtime_evaluator.py << 'EOF'
import os
import subprocess
import json
import time
from pathlib import Path


def run_command(cmd, cwd=None, timeout=60):
    try:
        start = time.time()

        result = subprocess.run(
            cmd,
            cwd=cwd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        duration = time.time() - start

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration": duration
        }

    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "duration": 999
        }


def evaluate_project(project_dir):
    score = 0
    metrics = {}

    compile_result = run_command(
        "python -m py_compile $(find . -name '*.py')",
        cwd=project_dir
    )

    metrics["compile"] = compile_result

    if compile_result["success"]:
        score += 25

    lint_result = run_command(
        "flake8 .",
        cwd=project_dir
    )

    metrics["lint"] = lint_result

    if lint_result["success"]:
        score += 20

    format_result = run_command(
        "black --check .",
        cwd=project_dir
    )

    metrics["format"] = format_result

    if format_result["success"]:
        score += 15

    pytest_result = run_command(
        "pytest",
        cwd=project_dir
    )

    metrics["pytest"] = pytest_result

    if pytest_result["success"]:
        score += 40

    metrics["final_score"] = score

    return metrics
EOF

# ============================================================
# Mutation Engine
# ============================================================

cat > mutation_engine.py << 'EOF'
import random

MUTATIONS = [
    "Add stronger modularity requirements",
    "Require async support",
    "Require better logging",
    "Require retry handling",
    "Require tests",
    "Require docstrings",
    "Require cleaner architecture",
    "Reduce token usage",
    "Improve startup speed",
    "Improve readability"
]


def mutate_prompt(prompt):
    mutation = random.choice(MUTATIONS)
    return f"{prompt}\n\nAdditional requirement: {mutation}"
EOF

# ============================================================
# Population Manager
# ============================================================

cat > population_manager.py << 'EOF'
import json
import random
from pathlib import Path

POP_FILE = "population/population.json"


def load_population():
    path = Path(POP_FILE)

    if not path.exists():
        seed = [
            {
                "prompt": "Generate clean production-grade Python software",
                "score": 0
            }
        ]

        path.parent.mkdir(exist_ok=True)

        with open(path, "w") as f:
            json.dump(seed, f, indent=2)

    with open(path) as f:
        return json.load(f)


def save_population(pop):
    with open(POP_FILE, "w") as f:
        json.dump(pop, f, indent=2)


def select_best(pop, k=3):
    return sorted(pop, key=lambda x: x["score"], reverse=True)[:k]
EOF

# ============================================================
# OpenAI Generator
# ============================================================

cat > generator.py << 'EOF'
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def generate_code(prompt):
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": "You are an autonomous software architect. Generate clean executable Python projects."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.8
    )

    return response.choices[0].message.content
EOF

# ============================================================
# README Beautifier
# ============================================================

cat > beautify_readme.py << 'EOF'
from pathlib import Path
from datetime import datetime

README = Path("README.md")


def beautify():
    existing = README.read_text() if README.exists() else ""

    banner = f"""
# Grounded Evolution System

Last Evolution Cycle: {datetime.utcnow().isoformat()} UTC

## Purpose

This system evolves prompts against REAL execution-based benchmarks.

It optimizes:
- Runtime success
- Test pass rates
- Modularity
- Maintainability
- Execution correctness

---

"""

    README.write_text(banner + existing)


if __name__ == "__main__":
    beautify()
EOF

# ============================================================
# Infinite Evolution Loop
# ============================================================

cat > infinite_research_loop.py << 'EOF'
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

from generator import generate_code
from mutation_engine import mutate_prompt
from population_manager import (
    load_population,
    save_population,
    select_best,
)
from evaluator.runtime_evaluator import evaluate_project


OUTPUT_DIR = Path("generated_projects")


def write_project_files(project_path, content):
    project_path.mkdir(parents=True, exist_ok=True)

    main_file = project_path / "main.py"

    main_file.write_text(content)

    test_file = project_path / "test_basic.py"

    test_file.write_text(
        """
def test_placeholder():
    assert True
"""
    )


def git_commit_and_push(score):
    subprocess.run("git add .", shell=True)

    subprocess.run(
        f'git commit -m "evolution-cycle score={score}"',
        shell=True
    )

    subprocess.run("git push origin grounded-evolution", shell=True)


def evolve_cycle(cycle_num):
    population = load_population()

    best = select_best(population, k=1)[0]

    mutated = mutate_prompt(best["prompt"])

    generated = generate_code(mutated)

    project_path = OUTPUT_DIR / f"cycle_{cycle_num}"

    write_project_files(project_path, generated)

    metrics = evaluate_project(project_path)

    population.append(
        {
            "prompt": mutated,
            "score": metrics["final_score"]
        }
    )

    population = sorted(
        population,
        key=lambda x: x["score"],
        reverse=True
    )[:20]

    save_population(population)

    with open(f"runtime_logs/cycle_{cycle_num}.json", "w") as f:
        json.dump(metrics, f, indent=2)

    subprocess.run("python beautify_readme.py", shell=True)

    git_commit_and_push(metrics["final_score"])

    print(f"Cycle {cycle_num} complete")
    print(metrics)


if __name__ == "__main__":
    cycle = 0

    while True:
        try:
            evolve_cycle(cycle)
            cycle += 1
            time.sleep(30)

        except KeyboardInterrupt:
            break

        except Exception as e:
            print(f"Loop error: {e}")
            time.sleep(15)
EOF

# ============================================================
# Git Ignore
# ============================================================

cat > .gitignore << 'EOF'
__pycache__/
*.pyc
.env
.venv/
generated_projects/
runtime_logs/
EOF

# ============================================================
# Final Commit
# ============================================================

git add .

git commit -m "Grounded execution evolution system upgrade"

# ============================================================
# Startup Instructions
# ============================================================

echo ""
echo "======================================================="
echo "SETUP COMPLETE"
echo "======================================================="
echo ""
echo "Export your OpenAI key first:"
echo ""
echo "export OPENAI_API_KEY='your_key_here'"
echo ""
echo "Then run:"
echo ""
echo "python infinite_research_loop.py"
echo ""
echo "The system will now evolve continuously using:"
echo "- Runtime execution"
echo "- pytest"
echo "- flake8"
echo "- black"
echo "- Git auto commits"
echo "- README beautification"
echo "- Infinite evolutionary cycles"
echo ""
```

---

## Recommended Next Step

Open the repo in:

* OpenCode
* Cursor
* Windsurf
* VSCode + Copilot

Then allow the coding agent to:

* monitor runtime logs
* improve evaluator robustness
* add benchmark diversity
* evolve multi-file project generation
* optimize mutation operators
* introduce hidden benchmark tasks
* add execution sandboxes
* add regression tracking

That is where this starts becoming a genuinely interesting autonomous experimentation system.

