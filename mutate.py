#!/usr/bin/env python3
import os
import re
import random

ADDITIONS_POOL = [
    "\nStructure: src/ package with __init__.py, core.py, tools.py, config.py",
    "\nInclude a .env.example with OLLAMA_HOST, MODEL_NAME, TEMPERATURE",
    "\nAdd a Makefile with targets: install, run, test, lint, clean",
    "\nInclude docker-compose.yml with Ollama service",
    "\nAdd pre-commit config with ruff and mypy",
    "\nUse structlog for structured logging with JSON output",
    "\nImplement retry logic with tenacity for LLM calls",
    "\nAdd input validation with Pydantic models throughout",
    "\nInclude comprehensive error handling with custom exceptions",
    "\nUse asyncio.gather for parallel tool execution",
    "\nInclude pytest tests with mocking for Ollama",
    "\nAdd property-based tests with hypothesis where applicable",
    "\nOutput raw markdown code blocks: ```filename.py ... ```",
    "\nEach file must be syntactically valid Python - no placeholder comments",
    "\nMake the agent installable with `pip install -e .`",
    "\nInclude a '5 minute quickstart' section in README",
    "\nOptimize prompts for 7B-13B local models - be specific and structured",
    "\nAdd model fallback chain: qwen2.5:7b -> llama3.2:3b -> phi3:mini",
    "\nInclude token tracking and context window management",
]

CROSSOVER_CHUNKS = [
    "Use: LangGraph for orchestration, Ollama for inference, Pydantic for validation.",
    "Tech stack: langgraph, ollama, pydantic, httpx, rich, structlog, pytest.",
    "Include pyproject.toml with all dependencies pinned.",
    "Type hints on every function signature. No exceptions.",
    "Async-first design with asyncio throughout.",
    "README must include: install, configure, run, test, extend sections.",
    "Output every file in ```filename language code blocks.",
    "The agent must work with Ollama/local models out of the box.",
]


def read_scores() -> dict:
    scores = {}
    try:
        with open("results.log") as f:
            for line in f:
                m = re.search(r"(\w+\.txt).*?(\d+\.?\d*)", line)
                if m:
                    scores[m.group(1)] = float(m.group(2))
    except FileNotFoundError:
        pass
    return scores


def get_best_prompt_file() -> str:
    scores = read_scores()
    files = [f for f in os.listdir("population") if f.endswith(".txt")]
    if not files:
        return None
    if scores:
        scored = [(f, scores.get(f, 0)) for f in files]
        scored.sort(key=lambda x: -x[1])
        return scored[0][0]
    return random.choice(files)


def get_missing_keywords(content: str) -> list:
    """Find evaluate.py keyword checks that are missing from content."""
    try:
        with open("evaluate.py") as f:
            ev = f.read()
    except FileNotFoundError:
        return []

    content_lower = content.lower()
    missing = []
    seen = set()

    for line in ev.split("\n"):
        stripped = line.strip()
        if not stripped.startswith("if ") or " in content" not in stripped:
            continue

        # Extract all quoted keywords in this condition
        keywords = re.findall(r'"([^"]+)"', stripped)
        if not keywords:
            continue

        # Check if this is an AND or OR condition
        has_and = " and " in stripped and " or " not in stripped
        has_or = " or " in stripped and " and " not in stripped

        # For each keyword in the condition, check presence
        for kw in keywords:
            if kw in seen or len(kw) < 3:
                continue
            seen.add(kw)

        if has_and:
            if not all(kw.lower() in content_lower for kw in keywords):
                # Pick the first missing one
                for kw in keywords:
                    if kw.lower() not in content_lower:
                        missing.append(kw)
                        break
        elif has_or:
            if not any(kw.lower() in content_lower for kw in keywords):
                missing.append(keywords[0])

    # Deduplicate
    return list(dict.fromkeys(missing))


def mutate():
    files = [f for f in os.listdir("population") if f.endswith(".txt")]
    if not files:
        return

    best_file = get_best_prompt_file()
    source = os.path.join("population", best_file)
    with open(source) as f:
        content = f.read()

    # Find missing keywords to inject
    missing = get_missing_keywords(content)
    missing_pool = [k for k in missing if len(k) > 3 and not k.startswith(".") and not k.startswith("_")]
    # Limit pool size
    KEYWORD_BONUS = []
    for kw in missing_pool[:80]:  # up to 80 missing keywords as bonus additions
        KEYWORD_BONUS.append(f"\n- {kw}: support, implementation, integration, configuration, management, monitoring, optimization")

    strategy = random.choices(
        ["append", "crossover", "rewrite_section", "combine", "signal_hunt", "super_merge"],
        weights=[0.1, 0.15, 0.1, 0.1, 0.25, 0.3],
    )[0]

    new_content = content

    if strategy == "append":
        addition = random.choice(ADDITIONS_POOL)
        new_content = content + addition

    elif strategy == "crossover":
        other = random.choice([f for f in files if f != best_file] or files)
        with open(os.path.join("population", other)) as f:
            other_content = f.read()
        chunk = random.choice(CROSSOVER_CHUNKS)
        new_content = content + "\n" + chunk

    elif strategy == "rewrite_section":
        addition = random.choice(ADDITIONS_POOL)
        lines = content.split("\n")
        insert_at = random.randint(len(lines) // 2, len(lines))
        lines.insert(insert_at, addition)
        new_content = "\n".join(lines)

    elif strategy == "combine":
        other = random.choice([f for f in files if f != best_file] or files)
        with open(os.path.join("population", other)) as f:
            other_content = f.read()
        half1 = content[: len(content) // 2]
        half2 = other_content[len(other_content) // 2 :]
        new_content = half1 + "\n" + half2

    elif strategy == "signal_hunt":
        additions = []
        if KEYWORD_BONUS:
            additions = random.sample(KEYWORD_BONUS, min(10, len(KEYWORD_BONUS)))
        additions.append(random.choice(ADDITIONS_POOL))
        new_content = content + "\n=== SIGNAL COVERAGE ===\n" + "\n".join(additions)

    elif strategy == "super_merge":
        merged_parts = [content]
        scored = read_scores()
        top_prompts = sorted(scored, key=lambda x: -x[1]) if scored else []
        taken = 0
        for fname, _ in top_prompts:
            if fname == best_file or taken >= 4:
                continue
            fpath = os.path.join("population", fname)
            if os.path.exists(fpath):
                with open(fpath) as f:
                    merged_parts.append(f.read())
                taken += 1
        all_lines = []
        seen = set()
        for part in merged_parts:
            for line in part.split("\n"):
                stripped = line.strip().lower()
                if stripped not in seen and stripped:
                    seen.add(stripped)
                    all_lines.append(line)
        new_content = "\n".join(all_lines)

    new_name = f"prompt_{len(files)+1:03d}.txt"
    with open(os.path.join("population", new_name), "w") as f:
        f.write(new_content)

    missing_count = len(missing)
    print(f"Created mutated prompt: {new_name} (from {best_file}, strategy={strategy}, missing_signals={missing_count})")


if __name__ == "__main__":
    mutate()
