"""Spearman correlation analysis: lexical vs grounded scores.

Usage:
    python analysis/correlation.py                  # Use cached grounded scores
    python analysis/correlation.py --refresh        # Re-run grounded eval for all prompts

Requires LLM_API_KEY to be set for the --refresh mode.
"""

import json
import sys
from pathlib import Path
from typing import Any


POPULATION_DIR: Path = Path("population")
POPULATION_JSON: Path = Path("population/population.json")
RESULTS_LOG: Path = Path("results.log")
GROUNDED_CACHE: Path = Path("analysis/grounded_scores_cache.json")


def load_lexical_scores() -> dict[str, float]:
    """Load lexical scores from results.log (lexical evaluation output)."""
    scores: dict[str, float] = {}
    if not RESULTS_LOG.exists():
        print("WARN: results.log not found — run evaluate.py first")
        return scores
    import re
    for line in RESULTS_LOG.read_text().splitlines():
        m = re.match(r"(\S+):\s*([\d.]+)", line)
        if m:
            scores[m.group(1)] = float(m.group(2))
    return scores


def load_grounded_scores() -> dict[str, float]:
    """Load previously cached grounded scores."""
    if GROUNDED_CACHE.exists():
        return json.loads(GROUNDED_CACHE.read_text())
    return {}


def save_grounded_scores(scores: dict[str, float]) -> None:
    """Cache grounded scores to disk."""
    GROUNDED_CACHE.parent.mkdir(exist_ok=True)
    GROUNDED_CACHE.write_text(json.dumps(scores, indent=2))


def evaluate_grounded(prompt_file: str) -> float | None:
    """Run a single prompt through the grounded evaluator.

    This requires a valid LLM_API_KEY. The prompt is sent to the LLM,
    the generated code is evaluated, and the execution score is returned.
    """
    prompt_path: Path = POPULATION_DIR / prompt_file
    if not prompt_path.exists():
        return None
    prompt_text: str = prompt_path.read_text()
    try:
        from generator import generate_code, write_project_files
        from evaluator.runtime_evaluator import evaluate_project
        import tempfile

        tmpdir: str = tempfile.mkdtemp(prefix="grounded_eval_")
        generated_text: str
        usage: dict[str, Any]
        generated_text, usage = generate_code(prompt_text, temperature=0.3)
        write_project_files(tmpdir, generated_text)
        metrics: dict[str, Any] = evaluate_project(tmpdir)
        return metrics.get("final_score", 0.0)
    except Exception as e:
        print(f"  ERROR evaluating {prompt_file}: {e}")
        return None


def compute_spearman(x: list[float], y: list[float]) -> float:
    """Compute Spearman rank correlation coefficient between two lists."""
    n: int = len(x)
    if n < 3:
        return 0.0

    from scipy.stats import spearmanr
    result = spearmanr(x, y)
    return float(result.statistic)


def main() -> None:
    """Compare lexical vs grounded scores across the population."""
    lexical: dict[str, float] = load_lexical_scores()
    if not lexical:
        print("No lexical scores found. Run evaluate.py first.")
        sys.exit(1)

    grounded: dict[str, float] = load_grounded_scores()
    refresh: bool = "--refresh" in sys.argv

    if refresh:
        grounded = {}
        print("Refreshing all grounded scores (this may take a while)...")
        prompt_files: list[str] = sorted(f.name for f in POPULATION_DIR.glob("*.txt"))
        for i, pf in enumerate(prompt_files):
            if pf in lexical:
                score = evaluate_grounded(pf)
                if score is not None:
                    grounded[pf] = score
                print(f"  [{i+1}/{len(prompt_files)}] {pf}: {grounded.get(pf, 'FAIL')}")
        save_grounded_scores(grounded)

    # Find prompts that have both lexical and grounded scores
    common: list[str] = sorted(set(lexical.keys()) & set(grounded.keys()))
    if not common:
        print("No prompts have both lexical and grounded scores.")
        print("Run with --refresh to compute grounded scores, or")
        print("set up the grounded loop and let it populate population.json.")
        sys.exit(1)

    lex_vals: list[float] = [lexical[p] for p in common]
    grd_vals: list[float] = [grounded[p] for p in common]

    print(f"\n{'='*60}")
    print(f"CORRELATION ANALYSIS: {len(common)} prompts")
    print(f"{'='*60}")
    print(f"{'Prompt':<25} {'Lexical':>8} {'Grounded':>10}")
    print(f"{'-'*25} {'-'*8} {'-'*10}")
    for p in common[:20]:
        print(f"{p:<25} {lexical[p]:>8.1f} {grounded[p]:>10.1f}")

    if len(common) > 20:
        print(f"  ... and {len(common) - 20} more")

    print(f"\nLexical  — min: {min(lex_vals):.1f}, max: {max(lex_vals):.1f}, mean: {sum(lex_vals)/len(lex_vals):.1f}")
    print(f"Grounded — min: {min(grd_vals):.1f}, max: {max(grd_vals):.1f}, mean: {sum(grd_vals)/len(grd_vals):.1f}")

    try:
        rho: float = compute_spearman(lex_vals, grd_vals)
        print(f"\nSpearman's ρ = {rho:.4f}")
        if abs(rho) < 0.2:
            print("Interpretation: Weak or no correlation — lexical and grounded scores")
            print("measure different things. This confirms the grounded loop is")
            print("capturing signal the lexical loop misses.")
        elif abs(rho) < 0.6:
            print("Interpretation: Moderate correlation — prompts that score well")
            print("lexically tend to produce better code, but with significant noise.")
        else:
            print("Interpretation: Strong correlation — lexical scoring may be a")
            print("sufficient proxy for execution quality in this domain.")
    except ImportError:
        print("\nInstall scipy for Spearman correlation: pip install scipy")
        print(f"Raw pair count: {len(common)}")


if __name__ == "__main__":
    main()
