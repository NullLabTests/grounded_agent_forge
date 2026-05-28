"""Population persistence and selection for the grounded evolution loop.

Manages a JSON-based population of prompts with their scores and
generation metadata. Supports elitist selection and tournament
selection strategies.
"""

import json
import random
from pathlib import Path


POP_FILE: str = "population/population.json"
MAX_POPULATION: int = 50

PopulationEntry = dict[str, str | float | int]
Population = list[PopulationEntry]


def load_population() -> Population:
    """Load population from JSON file, seeding if empty."""
    path = Path(POP_FILE)
    if not path.exists():
        seed: Population = [
            {
                "prompt": "Generate clean production-grade Python software with modular structure, type hints, and comprehensive tests",
                "score": 0,
                "generation": 0,
            }
        ]
        path.parent.mkdir(exist_ok=True)
        with open(path, "w") as f:
            json.dump(seed, f, indent=2)
        return seed
    with open(path) as f:
        return json.load(f)


def save_population(pop: Population) -> None:
    """Persist population to JSON file."""
    with open(POP_FILE, "w") as f:
        json.dump(pop, f, indent=2)


def select_best(pop: Population, k: int = 3) -> Population:
    """Return the top-k individuals by score (elitist selection)."""
    return sorted(pop, key=lambda x: float(x.get("score", 0)), reverse=True)[:k]


def select_tournament(pop: Population, tournament_size: int = 3) -> PopulationEntry:
    """Select via tournament: pick best from random subset."""
    competitors: Population = random.sample(pop, min(tournament_size, len(pop)))
    return max(competitors, key=lambda x: float(x.get("score", 0)))


def add_individual(pop: Population, prompt: str, score: float, generation: int) -> Population:
    """Add a new individual and cull to MAX_POPULATION."""
    pop.append(
        {
            "prompt": prompt,
            "score": score,
            "generation": generation,
        }
    )
    pop.sort(key=lambda x: float(x.get("score", 0)), reverse=True)
    return pop[:MAX_POPULATION]
