# Running the Evolution Loop with Coding Agents

This guide explains how to manually drive the prompt evolution loop using an AI coding assistant like OpenCode or Cursor.

## How It Works

You take the role of the **human evaluator** in the modify → evaluate → keep/revert loop:

1. **Modify** — Improve the prompt in `prompt.txt`
2. **Evaluate** — Run `python eval.py` to see the score
3. **Keep or Revert** — Commit improvements, revert regressions
4. **Repeat** — Iterate until the prompt is excellent

## Instructions

### Step 1: Open the Project

Open this repo in OpenCode or Cursor. The file you'll edit is `prompt.txt` at the repo root.

### Step 2: Improve the Prompt

Edit `prompt.txt` to make it better at generating AI agent projects. Some ideas:
- Add more specific instructions about project structure
- Request specific libraries or patterns (LangGraph, Pydantic, etc.)
- Clarify output format requirements (markdown code blocks)
- Add constraints about code quality, testing, or documentation

### Step 3: Evaluate

After each change, run:

```bash
python eval.py
```

The evaluator scores your prompt from **0–100** based on quality signals.

### Step 4: Keep or Revert

| Score | Action |
|-------|--------|
| **Higher than before** | Commit: `git add prompt.txt && git commit -m "Better prompt - score X"` |
| **Same or lower** | Revert: `git checkout prompt.txt` and try a different approach |

### Step 5: Repeat

Keep going for many iterations. Each generation brings you closer to the optimal prompt.

## Automated Evolution

For a fully automated version (no human needed), use `run_evolution.sh`. It uses a genetic algorithm with mutation, crossover, and selection — no manual editing required.

```bash
chmod +x run_evolution.sh
./run_evolution.sh
```

## Tips

- Make small, focused changes rather than rewriting the whole prompt
- Check `results.log` to track your score history
- The best prompts are specific, structured, and mention concrete libraries and patterns
- Focus on instructions that lead to production-ready, local-first agent projects
