import random

MUTATIONS = [
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

BENCHMARK_WEIGHTS = {
    "flask_api": 1.0,
    "cli_tool": 1.0,
    "websocket_server": 1.2,
    "data_processor": 0.8,
    "math_library": 0.8,
}


def mutate_prompt(prompt, benchmark_name=None):
    mutation = random.choice(MUTATIONS)
    result = f"{prompt}\n\nAdditional requirement: {mutation}"
    return result


def crossover_prompts(prompt_a, prompt_b):
    words_a = prompt_a.split()
    words_b = prompt_b.split()
    split_point = random.randint(len(words_a) // 4, 3 * len(words_a) // 4)
    result = " ".join(words_a[:split_point] + words_b[split_point:])
    return result


def get_mutation_pool():
    return MUTATIONS.copy()
