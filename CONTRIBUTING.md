# Contributing to Grounded Evolution

Thanks for considering contributing. This is an experimental research project, and contributions that improve the evolution system, documentation, or reproducibility are welcome.

## How to Contribute

### Improving the Evolution System

- **Add new signals**: Extend `SIGNAL_POOLS` in `auto_evolve.py` or add keyword checks to `evaluate.py`
- **Tune mutation weights**: Adjust strategy probabilities in `mutate.py` (line 130-133)
- **Write new strategies**: Add mutation strategies to `mutate.py` following the existing pattern
- **Improve runtime evaluator**: Extend `evaluator/runtime_evaluator.py` with more execution checks
- **Add benchmark tasks**: Add entries to `benchmarks/tasks.json`

### Documentation

- Improve README clarity and accuracy
- Add architecture decision records
- Improve code comments for non-obvious logic
- Document experiment results and observations

### Submitting Changes

1. Fork the repo and create a branch from `main`.
2. Make focused, single-purpose changes.
3. Test by running `python eval.py` to verify scoring still works.
4. If adding runtime features, run a quick validation cycle.
5. Open a pull request against `main`.

### Bug Reports & Feature Requests

Open an issue using the templates in `.github/ISSUE_TEMPLATE/`.

## Code Style

- **Python**: ruff-compatible. Run `ruff check .` before committing.
- **Keep files self-contained** when possible.
- **No exaggeration** in documentation — accurately describe capabilities.
- **Comments** for non-obvious behavior, not for basic operations.

## Research Integrity

- Do not claim AGI, sentience, or consciousness for this system.
- Frame contributions as evolutionary computation and prompt optimization research.
- Be honest about limitations and failure modes.

## Questions?

Open a [discussion](https://github.com/NullLabTests/grounded_evolution/discussions).
