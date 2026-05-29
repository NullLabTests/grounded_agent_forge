# Architecture (Legacy — Grounded Evolution)

> This document describes the architecture of the original `grounded_evolution` project.
> The current project (`grounded_agent_forge`) uses a new architecture centered on
> `agent_forge/orchestrator.py`. See [README.md](../README.md#architecture) for the current design.

## High-Level Design

Grounded Evolution uses a **dual-loop architecture** with two independent but cooperating evaluation systems:

```
┌──────────────────────────────────────────────────────────────┐
│                    GROUNDED EVOLUTION                         │
│                                                              │
│  ┌────────────────────────────┐  ┌────────────────────────┐  │
│  │   Lexical Loop (fast)      │  │  Grounded Loop (slow)  │  │
│  │                            │  │                        │  │
│  │  evaluate.py: 400+ signals │  │  generator.py: LLM     │  │
│  │  mutate.py: 5 strategies   │  │  runtime_evaluator.py  │  │
│  │  auto_evolve.py: meta      │  │  infinite_research_loop│  │
│  │  reflect.py: analysis      │  │  population_manager    │  │
│  │                            │  │  mutation_engine       │  │
│  └────────────────────────────┘  └────────────────────────┘  │
│           │                              │                    │
│           └────────── Shared ────────────┘                    │
│                      │                                       │
│                      ▼                                       │
│               population/ (150 prompts)                      │
│               population/population.json                     │
└──────────────────────────────────────────────────────────────┘
```

## Module Map

### Lexical Loop Modules

| Module | Lines | Role | Key Functions |
|--------|-------|------|---------------|
| `evaluate.py` | ~2000 | Lexical fitness function | `evaluate()`, `evaluate_population()` |
| `mutate.py` | 180 | Genetic mutation | `mutate()`, `get_missing_keywords()` |
| `reflect.py` | 270 | Generation analysis | `reflect()`, `get_current_scores()` |
| `auto_evolve.py` | 218 | Meta-evolution | `inject_new_signals()`, `main()` |
| `evolve_forever.py` | 654 | Aggressive meta-evolution | `inject_new_signals()`, `main()` |
| `eval.py` | 81 | Quick human-in-the-loop eval | — |

### Grounded Loop Modules

| Module | Lines | Role | Key Functions |
|--------|-------|------|---------------|
| `generator.py` | 235 | LLM code generation | `generate_code()`, `parse_code_blocks()`, `write_project_files()` |
| `runtime_evaluator.py` | 184 | Execution validation | `evaluate_project()`, `parse_syntax()`, `run_command()` |
| `infinite_research_loop.py` | 187 | Continuous evolution | `evolve_cycle()`, `main()` |
| `mutation_engine.py` | 55 | Prompt mutation operators | `mutate_prompt()`, `crossover_prompts()` |
| `population_manager.py` | 50 | Population persistence | `load_population()`, `save_population()`, `select_best()` |
| `beautify_readme.py` | 33 | README status updates | `beautify()` |

## Data Flow

### Lexical Flow

```
1. evaluate.py reads all files in population/
2. For each prompt file, scans for 400+ keywords
3. Scores each prompt (0–1000)
4. Writes results to results.log (ranked)
5. mutate.py reads results.log, picks best prompt
6. Applies one of 5 mutation strategies
7. Writes new prompt to population/prompt_NNN.txt
8. reflect.py reads population/, writes to reflection.md
9. auto_evolve.py periodically injects new signals into evaluate.py
```

### Grounded Flow

```
1. infinite_research_loop.py loads population from population.json
2. Selects best prompt via selection algorithm
3. Applies mutation or crossover via mutation_engine.py
4. Calls generator.py to generate code from prompt
5. Writes generated files to generated_projects/cycle_N/
6. Calls runtime_evaluator.py to validate execution
7. Computes total score = base + content_bonus
8. Updates population.json
9. Calls beautify_readme.py to update status
10. If score improved: git commit + push
11. Sleeps 10 seconds, repeats
```

## Scoring Systems

### Lexical Score (evaluate.py)

```
For each prompt file:
    score = 30.0 (baseline)
    for each keyword check:
        if keyword in prompt_text:
            score += 2
    return min(score, 1000)
```

### Execution Score (runtime_evaluator.py)

```
For each generated project:
    score = 0
    
    if ast.parse(all .py files) succeeds:     score += 20
    if functions >= 1:                        score += 5
    if classes >= 1:                          score += 5
    if pytest passes:                         score += 25
    elif pytest fails:                        score -= 5
    if flake8 passes:                         score += 10
    if main.py imports:                       score += 15
    if has test files:                        score += 5
    if has README:                            score += 2
    if has requirements.txt/pyproject.toml:   score += 3
    if file_count >= 3:                       score += 5
    
    return round(score, 1)
```

The total score in the grounded loop is `execution_score + content_bonus`, where `content_bonus` adds extra points for AST node count, function depth, etc.

## Meta-Evolution

When prompts saturate the scoring ceiling:

```
auto_evolve.py:
    - Maintains 10 signal pools (CI/CD, containers, databases, etc.)
    - Every N cycles, injects 6 random new signals into evaluate.py
    - Raises the scoring ceiling, forcing continued evolution

evolve_forever.py:
    - Extended version with 40+ signal pools (400+ signals)
    - Injects 15 signals every 3 cycles
    - Covers cloud, mobile, compliance, design patterns, etc.
```

## File Formats

### Population (population/population.json)

```json
[
  {
    "prompt": "Generate clean production-grade Python software...",
    "score": 862.0,
    "generation": 145
  }
]
```

### Runtime Log (runtime_logs/cycle_N.json)

```json
{
  "cycle": 42,
  "generation": 42,
  "benchmark": "flask_api",
  "base_score": 75.0,
  "content_bonus": 12.0,
  "total_score": 87.0,
  "files_generated": ["main.py", "test_basic.py"],
  "metrics": { ... },
  "timestamp": "2026-05-28T..."
}
```

### Results (results.log)

```
prompt_131.txt: 862.0
prompt_132.txt: 862.0
...
```

## Key Design Decisions

1. **Dual evaluation** — Lexical scoring is fast and cheap; execution scoring is slow but precise. Together they provide both breadth and depth.

2. **JSON-based population** — The grounded loop uses `population.json` (not individual `.txt` files) so it can track generation numbers and scores alongside prompts.

3. **Generator templates** — `generator.py` includes fallback templates in case the LLM call fails, ensuring the loop never crashes on API errors.

4. **Environment-based configuration** — All API keys and endpoints come from environment variables, making the system portable across providers.

5. **Auto-commit only on improvement** — The infinite loop only commits to git when scores increase, preventing noisy commit histories.

6. **README auto-update** — The status section of the README is updated after each grounded cycle, providing a live dashboard.
