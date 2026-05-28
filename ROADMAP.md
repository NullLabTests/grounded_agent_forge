# Grounded Evolution — Roadmap

> **Status**: Alpha — single-node evolution loop operational.

---

## Near-Term (v0.3 – v0.5)

- [ ] **Eval harness rewrite** — parameterized benchmarks so the score is meaningful across runs
- [ ] **Population persistence v2** — SQLite backend instead of JSON for concurrent access
- [ ] **Execution cost tracking** — log LLM tokens, wall time, and per-cycle cost to enable regression-aware pruning
- [ ] **Prompt diversity enforcement** — deduplicate near-identical prompts before insertion
- [ ] **Multi-provider LLM support** — graceful fallback if one provider is rate-limited
- [ ] **Explicit mutation hyper-parameters** — expose mutation rate, crossover rate, tournament size as CLI/env overrides
- [ ] **Regressions tests in CI** — run `evaluator/` suite on every PR

## Medium-Term (v0.6 – v1.0)

- [ ] **Parallel generation** — generate + evaluate multiple child prompts per cycle
- [ ] **Archive of generated projects** — retain every project artifact, not just the latest
- [ ] **Prompt migration** — keep a rolling window of high-scoring prompts; archive the rest
- [ ] **Human-in-the-loop** — optional approval gate before mutation is applied
- [ ] **Dashboard** — simple web UI for monitoring cycles, viewing generated projects, comparing scores
- [ ] **Git-based experiment tracking** — tag each commit with cycle metadata for reproducibility

## Long-Term (v1.0+)

- [ ] **Distributed evolution** — multiple agents running on different machines, sharing a common population DB
- [ ] **Cross-domain benchmarks** — evolve prompts for code, documentation YAML, SQL, shell scripts
- [ ] **Automated meta-parameter tuning** — treat mutation rate / temperature / selection pressure as evolvable parameters
- [ ] **LLM fine-tuning loop** — fine-tune a small adapter using high-scoring prompts as training data
