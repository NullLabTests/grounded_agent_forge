# Changelog

All notable changes to Grounded Evolution will be documented in this file.

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
