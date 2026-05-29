# AGENTS.md — Grounded Agent Forge Conventions

## Project Identity
This is a **research platform** for execution-grounded agent blueprint evolution.
Framing: evolutionary software optimization, NOT AGI/sentience claims.
Repository is public at `NullLabTests/grounded_agent_forge`.

## Code Style
- Type hints on **all** function signatures and public variables
- No comments unless absolutely necessary (the code should explain itself)
- Max line length: loosely 120 (no hard enforcement, follow existing style)
- Imports: stdlib, then blank line, then third-party, then blank line, then local
- Use `Any` from `typing` for dynamic types, never bare generics omitted
- Prefer `Path` from `pathlib` over `os.path`
- File-level docstrings on every `.py` file

## Project Structure
- `agent_forge/orchestrator.py` — Main evolution loop coordinator
- `agent_forge/agent_spec_generator.py` — Generates agent blueprints via LLM
- `agent_forge/full_agent_evaluator.py` — Multi-objective fitness evaluator (Docker sandbox)
- `agent_forge/meta_evolver.py` — Self-tuning evolution strategy adaptation
- `dashboard/main.py` — Real-time evolution visualization (FastAPI)
- `run_forge_loop.sh` — Bash automation wrapper

## Primary Focus
The `agent_forge/` module is the primary development focus. Legacy modules from
grounded_evolution (generator.py, mutation_engine.py, infinite_research_loop.py,
evaluator/, etc.) are maintained for reference but not actively developed.

## Environment Variables (never hardcode secrets)
- `LLM_API_KEY` — required for all LLM operations
- `LLM_MODEL` — model name (default: `deepseek-chat`)
- `LLM_BASE_URL` — API base URL (default: `https://api.deepseek.com/v1`)

## Git
- Commit on each major feature addition
- Auto-commits on score improvement from the evolution loop
- Commit messages: concise, descriptive, no emoji

## Adding New Features
1. Check if the feature already exists (grep for related terms)
2. Follow the existing pattern — if it's a mutation operator, add to meta_evolver.py
3. Type hints everywhere
4. Add environment variables to .env.example (never .env)
