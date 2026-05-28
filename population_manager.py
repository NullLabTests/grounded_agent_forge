import json
import random
from pathlib import Path

POP_FILE = "population/population.json"
MAX_POPULATION = 50


def load_population():
    path = Path(POP_FILE)
    if not path.exists():
        seed = [
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


def save_population(pop):
    with open(POP_FILE, "w") as f:
        json.dump(pop, f, indent=2)


def select_best(pop, k=3):
    return sorted(pop, key=lambda x: x.get("score", 0), reverse=True)[:k]


def select_tournament(pop, tournament_size=3):
    competitors = random.sample(pop, min(tournament_size, len(pop)))
    return max(competitors, key=lambda x: x.get("score", 0))


def add_individual(pop, prompt, score, generation):
    pop.append(
        {
            "prompt": prompt,
            "score": score,
            "generation": generation,
        }
    )
    pop.sort(key=lambda x: x.get("score", 0), reverse=True)
    return pop[:MAX_POPULATION]
