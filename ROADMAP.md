# Grounded Agent Forge — Roadmap

> **Status**: Pre-Alpha — scaffolding in place, core modules awaiting implementation.

---

## Near-Term — v1.0 (Implementation Phase)

- [ ] **Implement `orchestrator.py`** — evolution loop with selection, mutation, parallel generation
- [ ] **Implement `agent_spec_generator.py`** — LLM-based agent blueprint generation with structured output
- [ ] **Implement `full_agent_evaluator.py`** — Docker sandbox multi-objective fitness evaluator
- [ ] **Implement `meta_evolver.py`** — self-tuning mutation weights and strategy adaptation
- [ ] **Implement `dashboard/main.py`** — FastAPI-based real-time evolution visualization
- [ ] **Implement `run_forge_loop.sh`** — full automation wrapper with env validation
- [ ] **Blueprints registry** — SQLite-backed population persistence (FORGE_DB_URL)
- [ ] **CI integration** — automated forge module tests in GitHub Actions

## Medium-Term — v1.1 – v2.0

- [ ] **Task specialization** — population naturally diversifies into domain-specific agent archetypes
- [ ] **Multi-provider LLM support** — graceful fallback across providers
- [ ] **Agent archive** — retain every generated agent blueprint for analysis
- [ ] **Human-in-the-loop** — optional approval gate before agent execution
- [ ] **Benchmark suite expansion** — 20+ diverse agent tasks
- [ ] **Agent tournament** — head-to-head agent evaluation brackets
- [ ] **Git-based experiment tracking** — tag each cycle with full metadata

## Long-Term — v2.0+

- [ ] **Distributed evolution** — multiple forge instances sharing a population DB
- [ ] **Cross-domain agents** — evolve agents for code, data analysis, research, DevOps
- [ ] **Automated meta-parameter tuning** — treat mutation rate, temperature, selection pressure as evolvable
- [ ] **LLM fine-tuning loop** — fine-tune adapters using high-fitness agent blueprints as training data
- [ ] **Emergent tool creation** — agents that design and build their own tools
- [ ] **Published research** — paper with reproducible results and ablation studies
