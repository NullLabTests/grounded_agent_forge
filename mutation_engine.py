"""Prompt mutation operators for the grounded evolution loop.

Provides mutation and crossover functions that transform prompts
to explore the prompt fitness landscape. Includes self-tuning weights
that adapt based on mutation success rates over time.
"""

import json
import random
from pathlib import Path


MUTATION_WEIGHTS_FILE: Path = Path("memory/mutation_weights.json")


MUTATIONS: list[dict] = [
    {"desc": "Add stronger modularity requirements", "weight": 1.0},
    {"desc": "Require async support", "weight": 1.0},
    {"desc": "Require better logging with structured output", "weight": 1.0},
    {"desc": "Require retry handling with exponential backoff", "weight": 1.0},
    {"desc": "Require comprehensive tests with pytest", "weight": 1.0},
    {"desc": "Require docstrings on all public functions", "weight": 1.0},
    {"desc": "Require cleaner architecture with separation of concerns", "weight": 1.0},
    {"desc": "Reduce token usage and optimize for efficiency", "weight": 1.0},
    {"desc": "Improve startup speed and reduce imports", "weight": 1.0},
    {"desc": "Improve readability with clear naming conventions", "weight": 1.0},
    {"desc": "Add input validation using Pydantic or dataclasses", "weight": 1.0},
    {"desc": "Require type hints on all function signatures", "weight": 1.0},
    {"desc": "Add error handling with custom exceptions", "weight": 1.0},
    {"desc": "Require configuration via environment variables", "weight": 1.0},
    {"desc": "Add a Makefile with common development targets", "weight": 1.0},
    {"desc": "Require security best practices", "weight": 1.0},
    {"desc": "Add performance benchmarks", "weight": 1.0},
    {"desc": "Require Docker support with multi-stage builds", "weight": 1.0},
    {"desc": "Add CI/CD configuration", "weight": 1.0},
    {"desc": "Require API documentation with OpenAPI/Swagger", "weight": 1.0},
    {"desc": "Add database migration support", "weight": 1.0},
    {"desc": "Require monitoring and observability", "weight": 1.0},
    {"desc": "Add graceful shutdown handling", "weight": 1.0},
    {"desc": "Require dependency injection pattern", "weight": 1.0},
    {"desc": "Add feature flag support", "weight": 1.0},
]

_history: list[dict] = []


def _load_weights() -> None:
    """Load persisted mutation weights from disk."""
    global MUTATIONS
    if MUTATION_WEIGHTS_FILE.exists():
        try:
            stored: list[dict] = json.loads(MUTATION_WEIGHTS_FILE.read_text())
            for s in stored:
                for m in MUTATIONS:
                    if m["desc"] == s.get("desc"):
                        m["weight"] = s.get("weight", 1.0)
                        break
        except Exception:
            pass


def _save_weights() -> None:
    """Persist mutation weights to disk."""
    MUTATION_WEIGHTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        MUTATION_WEIGHTS_FILE.write_text(json.dumps(MUTATIONS, indent=2))
    except Exception:
        pass


def record_mutation_outcome(mutation_desc: str, score_delta: float) -> None:
    """Record a mutation's score impact for weight tuning.

    Call this after a generation completes with the score change
    relative to the parent prompt's score.
    """
    _history.append({"desc": mutation_desc, "delta": score_delta})
    if len(_history) >= 5:
        _tune_weights()


def _tune_weights() -> None:
    """Adjust mutation weights based on recent success history."""
    recent: list[dict] = _history[-20:]
    for m in MUTATIONS:
        records: list[dict] = [r for r in recent if r["desc"] == m["desc"]]
        if not records:
            continue
        avg_delta: float = sum(r["delta"] for r in records) / len(records)
        delta_weight: float = avg_delta / 10.0
        m["weight"] = max(0.1, min(5.0, m["weight"] + delta_weight))
    _save_weights()
    _history.clear()


def _weighted_choice() -> str:
    """Select a mutation using weighted random selection."""
    _load_weights()
    total: float = sum(m["weight"] for m in MUTATIONS)
    r: float = random.uniform(0, total)
    cumulative: float = 0.0
    for m in MUTATIONS:
        cumulative += m["weight"]
        if r <= cumulative:
            return m["desc"]
    return MUTATIONS[-1]["desc"]


def mutate_prompt(prompt: str, benchmark_name: str | None = None) -> tuple[str, str]:
    """Apply a random mutation to a prompt by appending a requirement.

    Returns (mutated_prompt, mutation_description).
    """
    mutation: str = _weighted_choice()
    return f"{prompt}\n\nAdditional requirement: {mutation}", mutation


def crossover_prompts(prompt_a: str, prompt_b: str) -> str:
    """Perform single-point crossover between two prompts."""
    words_a: list[str] = prompt_a.split()
    words_b: list[str] = prompt_b.split()
    split_point: int = random.randint(len(words_a) // 4, 3 * len(words_a) // 4)
    return " ".join(words_a[:split_point] + words_b[split_point:])


def get_mutation_pool() -> list[dict]:
    """Return the full mutation pool with current weights."""
    _load_weights()
    return MUTATIONS.copy()
