# Changelog

All notable changes to Grounded Agent Forge will be documented in this file.

## [1.0.0] - 2026-05-29

### Added
- ⚒️ Complete project rebrand from `grounded-evolution` to `grounded-agent-forge`
- 🧬 `agent_forge/` module with full blueprint evolution architecture:
  - `orchestrator.py` — Main evolution loop coordinator
  - `agent_spec_generator.py` — Agent blueprint generation via LLM
  - `full_agent_evaluator.py` — Multi-objective fitness evaluator (Docker sandbox)
  - `meta_evolver.py` — Self-tuning evolution strategy adaptation
- 📊 `dashboard/main.py` — Real-time evolution visualization (FastAPI)
- 🐚 `run_forge_loop.sh` — Bash automation wrapper
- 📝 Complete README with badges, lineage section, DeepSeek V4 credit, and architecture docs
- 🔄 GitHub repository `NullLabTests/grounded_agent_forge` with 10 topics
- 📋 Updated CI workflow covering forge modules
- 🔧 Updated `.env.example` with DeepSeek defaults
- 📦 Updated `pyproject.toml` with forge dependencies (sqlalchemy, fastapi, docker, httpx, rich)
- 🤝 Updated CONTRIBUTING.md for forge project
- 🔒 Updated SECURITY.md for forge project

### Changed
- Remote URL from `grounded_evolution` to `grounded_agent_forge`
- Default LLM model from `mistral-large-latest` to `deepseek-chat`
- Default LLM base URL from `api.mistral.ai` to `api.deepseek.com`

## [0.2.1] - 2026-05-28

### Added
- Type hints to all core modules: generator, infinite_research_loop, runtime_evaluator, mutation_engine, population_manager, beautify_readme, regression_tracker
- `.github/CODEOWNERS`, `FUNDING.yml`, `dependabot.yml` — repository governance
- ROADMAP.md — near/medium/long-term development plan
- EVOLUTION_REPORT.md — complete experiment summary with grounded/lexical analysis
- `super_merge` mutation strategy — combines top-5 prompts for plateau breaking
- Auto-detection of real scores in beautify_readme.py (reads population.json)

### Changed
- Fixed stale score marker in auto_evolve.py (500→1000)
- Updated all stale URLs to grounded_evolution (SECURITY.md, config.yml, badge.yml, script.sh)
- beautify_readme.py now non-destructive (marker-based section update)
- generator.py uses env-var LLM config (LLM_API_KEY, LLM_MODEL, LLM_BASE_URL) — no hardcoded keys
- requirements.txt pinned with versions
- README badges/metrics updated to 163 prompts

### Fixed
- `datetime.UTC` → `datetime.timezone.utc` in regression_tracker.py (Python 3.14 compat)

## [0.2.0] - 2026-05-28

### Added
- Repository initialized as `grounded_evolution` on NullLabTests
- Dual evaluation system documented: lexical + execution-grounded
- Architecture diagrams in mermaid
- Results tracking with score distribution
- Research context and framing documentation
- CHANGELOG and improved CONTRIBUTING guide
- CI/CD and issue templates preserved from upstream

### Changed
- Project renamed from `autoresearch-ai-agent-skeleton` to `grounded-evolution`
- README significantly expanded with detailed architecture, results, and customization docs
- Repository structure flattened for clarity
- Documentation improved for professional research presentation

### Legacy (v0.1.x)

The project was originally developed as `autoresearch-ai-agent-skeleton` with:
- 150 generations of prompt evolution
- 400+ lexical scoring signals
- 5-strategy genetic mutation engine
- Meta-evolution with automatic signal injection
- Execution-grounded runtime validation
