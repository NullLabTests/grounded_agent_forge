# Contributing to Grounded Agent Forge

Thanks for considering contributing. This is an experimental research project exploring how genetic algorithms can evolve complete agent architectures. Contributions that improve the evolution system, agent quality, documentation, or reproducibility are welcome.

## How to Contribute

### Improving the Evolution System

- **Add mutation operators**: Extend `agent_forge/meta_evolver.py` with new crossover/mutation strategies
- **Improve agent evaluation**: Extend `agent_forge/full_agent_evaluator.py` with new fitness dimensions
- **Enhance agent specs**: Add new blueprint components to `agent_forge/agent_spec_generator.py`
- **Tune meta-evolution**: Adjust adaptation rates and operator weightings in `meta_evolver.py`
- **Add benchmark tasks**: Contribute new benchmark definitions to `benchmarks/tasks.json`
- **Improve the dashboard**: Extend `dashboard/main.py` with new visualizations

### Documentation

- Improve README clarity and accuracy
- Add architecture decision records
- Document experiment results and observations
- Improve code quality (type hints, self-documenting patterns)

### Submitting Changes

1. Fork the repo and create a branch from `main`.
2. Make focused, single-purpose changes.
3. Follow the code style (ruff-compatible Python).
4. Verify with lint:
   ```bash
   ruff check agent_forge/ dashboard/
   ```
5. Open a pull request against `main`.

### Bug Reports & Feature Requests

Open an issue using the templates in `.github/ISSUE_TEMPLATE/`.

## Code Style

- **Python**: ruff-compatible. Run `ruff check .` before committing.
- **Type hints** on all function signatures and public variables.
- **No comments** unless absolutely necessary (the code should explain itself).
- **No exaggeration** in documentation — accurately describe capabilities.

## Research Integrity

- This is evolutionary software optimization research, not AGI.
- Do not claim sentience, consciousness, or general intelligence.
- Frame contributions as evolutionary computation research.
- Be honest about limitations and failure modes.

## Questions?

Open a [discussion](https://github.com/NullLabTests/grounded_agent_forge/discussions).
