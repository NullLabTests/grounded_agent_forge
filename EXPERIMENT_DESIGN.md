# Experiment Design

This document describes the experimental framework for studying execution-grounded
prompt evolution. The goal is to move from a research prototype to a reproducible
experiment with publishable results.

## Research Questions

1. **Does execution-grounded scoring select for different prompts than lexical scoring?**
   - Hypothesis: Lexical and grounded scores are weakly correlated (Spearman ρ < 0.3).
   - A prompt that "reads well" (mentions many keywords) does not necessarily produce
     good code. The grounded loop should surface prompts that produce correct, testable,
     well-structured output — even if they are shorter and less keyword-dense.

2. **Does grounded evolution improve generated code quality across generations?**
   - Hypothesis: Grounded scores increase over successive evolution cycles,
     with diminishing returns after 50–100 cycles per benchmark.

3. **Which mutation operator contributes most to grounded score improvement?**
   - Ablation: run with mutation only, crossover only, and both disabled (random walk).
   - Compare convergence rates and final scores.

## Benchmarks

Three benchmarks, each with real hidden test code that validates behavior:

| Benchmark | Domain | Hidden tests | Max score |
|-----------|--------|-------------|-----------|
| `cli_task_manager` | CLI tool with argparse | Add/list/complete/delete tasks | 100 |
| `async_web_scraper` | Async HTTP with rate limiting | Concurrent fetch, error handling, rate limit | 100 |
| `data_pipeline` | CSV→transform→JSON pipeline | Read, filter, aggregate, write | 100 |

Hidden test files live inside `benchmarks/tasks.json` as `hidden_test_files`.
They are copied into the generated project directory before pytest runs.

## Metrics

Per-cycle logging (JSONL at `experiments/run_log.jsonl`):

| Field | Source | Description |
|-------|--------|-------------|
| `score` | runtime_evaluator | Composite execution score (0–100) |
| `syntax_valid` | AST parser | Whether all .py files parse |
| `pytest_pass` | pytest | Whether all tests pass |
| `hidden_tests_pass` | hidden tests | Whether benchmark behavioral tests pass |
| `mutation` | mutation_engine | Which operator was applied |
| `llm_total_tokens` | generator | Total LLM tokens consumed |
| `llm_duration_s` | generator | Wall time for LLM generation |
| `cycle_duration_s` | timed | Total cycle wall time |
| `ast_nodes` | AST counter | Code complexity proxy |
| `functions` / `classes` | AST counter | Code structure proxy |

## Archiving

Every generated project is archived to `experiments/projects/{benchmark}/cycle_{n:04d}/`
with full source code and a `metadata.json`. This enables manual review of top-10
vs bottom-10 outputs.

## Ablation Studies

Configure by setting `ABLATION` flags in `infinite_research_loop.py`:

```python
ABLATION = {
    "mutation": True,      # toggle prompt mutation
    "crossover": True,     # toggle prompt crossover
    "mutation_rate": 0.7,  # probability of mutation when both enabled
}
```

Four conditions, each run for 100 cycles per benchmark:

| Condition | mutation | crossover | Expectation |
|-----------|----------|-----------|-------------|
| Full | True | True | Best convergence (baseline) |
| Mutation only | True | False | Tests crossover contribution |
| Crossover only | False | True | Tests mutation contribution |
| Random walk | False | False | No-op baseline (chance improvement) |

## Procedure

1. Run 100 grounded cycles per benchmark (full config) → ~300 cycles total
2. Run 100 grounded cycles per ablation condition → ~1200 cycles total
3. Run Spearman correlation (`analysis/correlation.py --refresh`)
4. Manually review top-10 and bottom-10 generated projects from each condition
5. Publish results with score distributions, convergence curves, and qualitative analysis

## Files

| File | Purpose |
|------|---------|
| `experiments/run_log.jsonl` | Per-cycle structured log |
| `experiments/projects/` | Archived generated projects |
| `analysis/correlation.py` | Spearman ρ computation |
| `benchmarks/tasks.json` | Benchmark + hidden test definitions |
| `infinite_research_loop.py` | Experiment runner (main entry point) |
