# Comparison: Lexical-Only vs Execution-Grounded Evolution (Legacy)

> This document explains the key differences between the original `autoresearch-ai-agent-skeleton` and
> `grounded_evolution` approaches. The current project (`grounded_agent_forge`) evolves full agent blueprints
> rather than just prompts. See [README.md](../README.md#project-lineage) for the current comparison.

This document explains the key differences between the original `autoresearch-ai-agent-skeleton` approach (lexical-only) and the Grounded Evolution approach (execution-grounded).

## Why This Comparison Matters

The original system pioneered **evolutionary prompt optimization** — using genetic algorithms to find prompts that score well on keyword-coverage metrics. It proved the concept.

Grounded Evolution extends that work by answering a harder question: **do prompts that *mention* the right things actually *produce* good code?**

## Core Difference

| Aspect | Lexical-Only | Execution-Grounded |
|--------|-------------|-------------------|
| **What is scored** | The prompt text itself | The prompt text + the code it generates |
| **Fitness signal** | Keyword presence/absence | Keyword presence + AST validity + test pass rate + code structure |
| **Code generation** | Never generates code | Generates real projects via LLM |
| **Validation** | Text matching | Real execution (compile, test, lint) |
| **Loop type** | Finite generations | Infinite continuous evolution |
| **Commit strategy** | Manual | Auto-commit on improvement |
| **Meta-evolution** | Inject new keywords | Inject new keywords + update README + commit |

## Architectural Differences

### Lexical-Only Pipeline

```
Population → mutate() → evaluate() → reflect() → repeat
                           │
                           ▼
                    Keyword checks on
                    prompt TEXT only
```

All four core modules (`mutate.py`, `evaluate.py`, `reflect.py`, `auto_evolve.py`) operate exclusively on **text**. They never invoke an LLM, never generate code, never run a test suite.

### Execution-Grounded Pipeline

```
Population → mutate() → evaluate() ──┐
                           │         │
                           ▼         ▼
                    Keyword checks   generator.py
                    on prompt TEXT    │
                                     ▼
                              LLM generates
                              project files
                                     │
                                     ▼
                              runtime_evaluator.py
                              ├── AST parse (valid Python?)
                              ├── pytest (do tests pass?)
                              ├── flake8 (PEP 8 compliant?)
                              └── structure (well-organized?)
                                     │
                                     ▼
                              Execution score
                              feeds back to
                              population
```

The grounded pipeline adds an entire execution layer. Prompts are not just read — they're used to generate real code, and that code is validated by running it.

## What Each System Actually Scores

### Lexical-Only Scoring

```python
# Is this keyword in the prompt text?
if "pytest" in prompt_text:
    score += 2
if "docker" in prompt_text:
    score += 2
# ... 400 more checks like this
```

**Limitation**: A prompt could say "use pytest" but the generated code might have no tests, or tests that fail. The lexical score wouldn't catch this.

### Execution-Grounded Scoring

```python
# Step 1: Generate code from prompt
generated_code = llm.generate(prompt)
project_files = write_to_disk(generated_code)

# Step 2: Validate execution
syntax_result = ast.parse(project_files)        # Does it compile?
test_result = pytest.run(project_files)          # Do tests pass?
lint_result = flake8.run(project_files)          # Is it clean?
structure = analyze_structure(project_files)     # Is it well-organized?

# Step 3: Score based on real outcomes
score += 20 if syntax_result.valid else 0
score += 25 if test_result.passed else -5
score += 10 if lint_result.clean else 0
# ... more structural metrics
```

## What This Means for Evolution

### Lexical-Only Evolution

The system optimizes prompts to **mention** the right things. If "kubernetes" gives +2 points, the system will evolve prompts that mention kubernetes. This is useful for:

- Discovering what vocabulary correlates with good prompts
- Creating comprehensive specification-style prompts
- Understanding what concepts differentiate prompt quality

### Execution-Grounded Evolution

The system optimizes prompts to **produce** code that works. Key difference:

- Mentioning "pytest" doesn't help unless the generated code actually has passing tests
- Mentioning "type hints" doesn't help unless the generated code actually has type annotations
- The LLM's actual behavior with a given prompt determines the score

## Practical Implications

| Scenario | Lexical-Only | Execution-Grounded |
|----------|-------------|-------------------|
| Prompt says "use pytest" but generates no tests | +2 points (keyword match) | 0 points (no test files) |
| Prompt says "type hints" but generates untyped code | +2 points | 0 points |
| Prompt is brief but generates excellent code | Low score (few keywords) | High score (code works) |
| Prompt is verbose keyword salad | High score (many keywords) | Variable (depends on generation) |

## When to Use Each

**Use lexical-only when:**
- You want to understand what vocabulary drives prompt quality
- You're doing rapid iteration on prompt structure
- You don't have LLM API access for generation
- You're benchmarking prompt content, not generation outcomes

**Use execution-grounded when:**
- You want prompts that produce *working* code
- You have LLM API access
- You care about actual code quality, not just prompt wording
- You want continuous, autonomous optimization

## Combined Approach (What This Repo Does)

This repo runs **both** scoring systems:

1. **Lexical scoring** (fast, cheap, broad) — 400+ keyword signals score the prompt text
2. **Execution scoring** (slow, expensive, precise) — generates code, runs it, scores outcomes

Together they provide:
- Rapid exploration via lexical scoring
- Precise validation via execution scoring
- Resistance to keyword-stuffing optimizations
- Grounding in real code quality
