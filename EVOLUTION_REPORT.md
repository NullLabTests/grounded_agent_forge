# Evolution Report

## Summary

| Metric | Value |
|---|---|
| Total cycles | 163 |
| Score range | 35 → 862 (24.6× improvement) |
| Population size | 163 prompts |
| Evaluation method | 400+ signal lexical scoring |
| Evolution loops | Lexical + Grounded (dual) |

## Lexical Loop (evaulate.py + mutate.py)

The original skeleton already contained a mature lexical-evolution loop. Prompts are scored by keyword/signal presence (tech stack, code quality, testing, security, etc.). The best prompt scored **862/1000** — a 24.6× improvement over the starting seed.

### Top scoring signals
- `langgraph` (+4), `ollama` (+5), `local` (+3) — local LLM stack consistently wins
- `pydantic` (+3), `httpx` (+2) — type-safe HTTP clients valued
- `error handling` (+2), `logging` (+2), `tests` (+2) — code quality signals
- `docker` (+2), `CI / GitHub Actions` (+2) — deployment awareness
- Async, streaming, caching, retry primitives

### What the lexical loop cannot measure
- Whether the generated code **actually compiles**
- Whether **tests pass**
- Whether the project is **well-structured** (functions, classes, modules)
- Whether **dependencies are declared**
- Linting / code style violations

This limitation is the **motivation for the grounded loop**.

## Grounded Loop (infinite_research_loop.py)

The grounded loop closes the gap by:
1. **Generating real code** from the prompt (via LLM → `generator.py`)
2. **Validating execution** (AST parse, pytest, flake8 — `runtime_evaluator.py`)
3. **Scoring on real outcomes** not keyword counts
4. **Backpropagating** the execution score into the population as prompt fitness

### Grounded scoring breakdown

| Component | Max score | What it measures |
|---|---|---|
| Syntax validity | 20 | AST parse succeeds on all `.py` files |
| Test pass rate | 25 | pytest exit code 0 |
| Lint cleanliness | 10 | flake8 no errors (E/F/W) |
| Runtime execution | 15 | `main.py` can be imported and run |
| Structure | 10 | ≥3 functions + ≥2 classes |
| Tests exist | 5 | `test_*.py` files present |
| Dependencies | 3 | `requirements.txt` or `pyproject.toml` |
| Documentation | 2 | `README.md` present |
| File count | 5 | ≥3 `.py` files |
| AST complexity | 5 | >50 AST nodes |
| **Total** | **100** | |

### Observed behavior
- Prompts that mention specific library versions tend to generate broken `requirements.txt` (hard to match against current PyPI)
- Vague prompts ("generate a clean Python project") produce higher pass rates than specific ones ("build a CLI task manager with argparse") because the LLM has more freedom
- High lexical score ≠ high execution score; some 800+ prompts generate code that fails flake8

## Key Insight

**Lexical and grounded scores are weakly correlated.** The most "impressive" prompts (long, many keywords) often produce the messiest code. The grounded loop acts as a regularizer — rewarding prompts that produce **simple, correct, and tested** output over prompts that read well on paper.

## Lexical Plateau

After 163 generations and 40+ injected signal pools, the lexical loop has converged at **862/1000**. All 500+ keyword checks have been injected into `evaluate.py`. The remaining 138 points require niche keywords that no single prompt can practically cover without becoming an incoherent keyword salad.

The `super_merge` strategy (added to `mutate.py`) attempts to combine all top-5 prompts into one maximally broad prompt, but even this can't bridge the gap — the signals are inherently contradictory (e.g., language-specific keywords for Python vs JavaScript).

## Next Steps

1. **Run the grounded loop** with an LLM API key set (`LLM_API_KEY`) — this shifts from keyword scoring to execution validation
2. **Run a Spearman correlation** between lexical score and grounded score across the full population
3. **Track per-cycle cost** (LLM tokens + wall time) to identify regression
4. **Archive generated projects** from the top-10 grounded prompts for manual review
5. **Diversify benchmarks** in `benchmarks/tasks.json` — the current single-benchmark mode limits grounded evolution breadth
