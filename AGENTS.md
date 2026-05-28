# AGENTS.md — Grounded Evolution Conventions

## Project Identity
This is a **research platform** for execution-grounded prompt evolution.
Framing: evolutionary software optimization, NOT AGI/sentience claims.
Repository is public at `NullLabTests/grounded_evolution`.

## Conventions

### Code Style
- Type hints on **all** function signatures and public variables
- No comments unless absolutely necessary (the code should explain itself)
- Max line length: loosely 120 (no hard enforcement, follow existing style)
- Imports: stdlib, then blank line, then third-party, then blank line, then local
  (stdlib comes first; no `isort`/`ruff` ordering enforced — be practical)
- Use `Any` from `typing` for dynamic types, never bare generics omitted
- Prefer `Path` from `pathlib` over `os.path`
- File-level docstrings on every `.py` file

### Project Structure
- `generator.py` — LLM code generation, returns `(text, usage_dict)` tuple
- `evaluator/runtime_evaluator.py` — execution-grounded validation (AST, pytest, hidden tests)
- `mutation_engine.py` — prompt mutation/crossover operators
- `mutation.py` / `evaluate.py` / `evolve_forever.py` / `auto_evolve.py` — lexical-only loop (legacy)
- `population_manager.py` — JSON-based population persistence
- `infinite_research_loop.py` — main grounded loop (calls generator → evaluator → population_manager)
- `run_experiment.py` — orchestrated ablation experiments
- `benchmarks/tasks.json` — 3 benchmark definitions with inline hidden test files
- `experiments/` — all experiment output (logs, archives, ablation runs)

### Two Loops
1. **Lexical loop** (`evaluate.py`/`evolve_forever.py`): keyword-matching fitness. Currently at 218 prompts, best score 1000/1000. Less important now.
2. **Grounded loop** (`infinite_research_loop.py`/`generator.py`/`runtime_evaluator.py`): real code execution fitness. This is the primary focus.

### Environment Variables (never hardcode secrets)
- `LLM_API_KEY` — required for grounded loop
- `LLM_MODEL` — model name (default: `mistral-large-latest`)
- `LLM_BASE_URL` — API base URL (default: `https://api.mistral.ai/v1`)

### Testing
- No test suite for the project itself yet (TODO for future)
- Hidden benchmark tests live in `benchmarks/tasks.json` as `hidden_test_files` dict
- Rust-based tests (`cargo test`) exist in the `generated_projects/` output (not our code)

### Git
- Auto-commits on score improvement from the grounded loop
- Manual commits for structural changes (new features, refactors, docs)
- Commit messages: concise, descriptive, no emoji

### Adding New Features
1. Check if the feature already exists (grep for related terms)
2. Follow the existing pattern (if it's a mutation, add to `mutation_engine.py`)
3. Type hints everywhere
4. Add the new feature to `run_experiment.py` if it's an experimental variable
5. Update EXPERIMENT_DESIGN.md if the experiment protocol changes
