"""Prompt mutation operators for the grounded evolution loop.

Provides mutation and crossover functions that transform prompts
to explore the prompt fitness landscape.
"""

import random


MUTATIONS: list[str] = [
    "Add stronger modularity requirements",
    "Require async support",
    "Require better logging with structured output",
    "Require retry handling with exponential backoff",
    "Require comprehensive tests with pytest",
    "Require docstrings on all public functions",
    "Require cleaner architecture with separation of concerns",
    "Reduce token usage and optimize for efficiency",
    "Improve startup speed and reduce imports",
    "Improve readability with clear naming conventions",
    "Add input validation using Pydantic or dataclasses",
    "Require type hints on all function signatures",
    "Add error handling with custom exceptions",
    "Require configuration via environment variables",
    "Add a Makefile with common development targets",
    "Require security best practices",
    "Add performance benchmarks",
    "Require Docker support with multi-stage builds",
    "Add CI/CD configuration",
    "Require API documentation with OpenAPI/Swagger",
    "Add database migration support",
    "Require monitoring and observability",
    "Add graceful shutdown handling",
    "Require dependency injection pattern",
    "Add feature flag support",
]

BENCHMARK_WEIGHTS: dict[str, float] = {
    "cli_task_manager": 1.0,
    "async_web_scraper": 1.2,
    "data_pipeline": 1.0,
}


def mutate_prompt(prompt: str, benchmark_name: str | None = None) -> str:
    """Apply a random mutation to a prompt by appending a requirement."""
    mutation: str = random.choice(MUTATIONS)
    return f"{prompt}\n\nAdditional requirement: {mutation}"


def crossover_prompts(prompt_a: str, prompt_b: str) -> str:
    """Perform single-point crossover between two prompts."""
    words_a: list[str] = prompt_a.split()
    words_b: list[str] = prompt_b.split()
    split_point: int = random.randint(len(words_a) // 4, 3 * len(words_a) // 4)
    return " ".join(words_a[:split_point] + words_b[split_point:])


def get_mutation_pool() -> list[str]:
    """Return the full mutation pool."""
    return MUTATIONS.copy()
