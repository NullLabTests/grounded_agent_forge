#!/usr/bin/env python3
"""Simple prompt evaluator for the outer loop (manual evolution).

Scores a prompt based on quality signals: tech stack, code quality,
testing, security, documentation, and more. Max score: 100.
"""

import os
from datetime import datetime


def evaluate() -> float:
    prompt_path = "prompt.txt"
    if not os.path.exists(prompt_path):
        print("No prompt.txt found. Create one first.")
        return 0.0

    raw = open(prompt_path).read()
    content = raw.lower()
    score = 30.0

    # --- Tech stack ---
    if "ollama" in content: score += 5
    if "local" in content: score += 3
    if "langgraph" in content: score += 4
    if "react" in content or "react loop" in content: score += 3
    if "pydantic" in content: score += 3
    if "httpx" in content: score += 2

    # --- Quality ---
    if "pyproject.toml" in content: score += 4
    if "type hint" in content or "type hints" in content: score += 3
    if "error handling" in content: score += 2
    if "logging" in content: score += 2
    if "test" in content or "tests" in content: score += 2
    if "async" in content: score += 2
    if "streaming" in content or "stream" in content: score += 2
    if "retry" in content: score += 2
    if "main()" in content or "__main__" in content: score += 2
    if "dataclass" in content: score += 2
    if "docstring" in content: score += 2

    # --- Output ---
    if "```" in content: score += 4
    if "readme" in content or "README" in raw: score += 3
    if "install" in content or "pip install" in content: score += 2

    # --- Completeness ---
    words = len(content.split())
    if words > 100: score += 2
    if words > 200: score += 2
    if words > 300: score += 2

    # --- Security ---
    if "auth" in content or "authentication" in content: score += 2
    if "api key" in content or "secret" in content: score += 2

    # --- Performance ---
    if "cache" in content: score += 2
    if "parallel" in content or "concurrent" in content: score += 2

    # --- Deployment ---
    if "docker" in content: score += 2
    if "ci" in content or "github action" in content: score += 2
    if "makefile" in content: score += 2

    score = min(100.0, round(score, 1))
    timestamp = datetime.now().isoformat()

    with open("results.log", "a") as f:
        f.write(f"{timestamp} | Score: {score}/100\n")

    print(f"Score: {score}/100")
    print(f"Prompt: {len(words)} words, {len(content)} chars")
    print("Logged to results.log")
    return score


if __name__ == "__main__":
    evaluate()
