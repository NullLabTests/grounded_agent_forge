"""Generate a markdown summary report from the experiment log.

Reads experiments/run_log.jsonl and prints a formatted report
to stdout with trend analysis and cycle breakdown.
"""

import json
from collections import Counter
from pathlib import Path
from typing import Any


EXPERIMENT_LOG: Path = Path("experiments/run_log.jsonl")
REPORT_FILE: Path = Path("reports/evolution_summary.md")


def load_entries() -> list[dict[str, Any]]:
    """Load all experiment log entries."""
    entries: list[dict[str, Any]] = []
    if not EXPERIMENT_LOG.exists():
        return entries
    with open(EXPERIMENT_LOG) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries


def generate_report(entries: list[dict[str, Any]]) -> str:
    """Generate a markdown report from experiment entries."""
    if not entries:
        return "# Evolution Summary\n\nNo cycles completed yet.\n"

    scores: list[float] = [e.get("score", 0) for e in entries]
    avg_score: float = sum(scores) / len(scores) if scores else 0
    best: dict[str, Any] = max(entries, key=lambda e: e.get("score", 0))
    worst: dict[str, Any] = min(entries, key=lambda e: e.get("score", 0))
    benchmark_counts: Counter = Counter(e.get("benchmark", "unknown") for e in entries)
    mutation_counts: Counter = Counter(e.get("mutation", "none") for e in entries)

    last_10: list[float] = scores[-10:] if len(scores) >= 10 else scores
    first_10: list[float] = scores[:10] if len(scores) >= 10 else scores

    lines: list[str] = [
        "# Evolution Summary",
        "",
        f"**Generated:** {entries[-1].get('timestamp', 'unknown')}",
        f"**Total cycles:** {len(entries)}",
        f"**Score range:** {min(scores):.1f} – {max(scores):.1f}",
        f"**Average score:** {avg_score:.1f}",
        f"**Best:** Cycle {best.get('cycle', '?')} ({best.get('benchmark', '?')}) = {best.get('score', '?')}",
        f"**Worst:** Cycle {worst.get('cycle', '?')} ({worst.get('benchmark', '?')}) = {worst.get('score', '?')}",
        "",
    ]

    if first_10 and last_10 and len(scores) >= 5:
        first_avg: float = sum(first_10) / len(first_10)
        last_avg: float = sum(last_10) / len(last_10)
        delta: float = last_avg - first_avg
        trend: str = "upward" if delta > 1 else "downward" if delta < -1 else "flat"
        lines.append(f"**Trend:** {trend} (first {len(first_10)} avg={first_avg:.1f}, last {len(last_10)} avg={last_avg:.1f})")
        lines.append("")

    lines.append("## Benchmark Usage")
    lines.append("")
    lines.append("| Benchmark | Cycles |")
    lines.append("|-----------|--------|")
    for bm, count in benchmark_counts.most_common():
        lines.append(f"| {bm} | {count} |")
    lines.append("")

    lines.append("## Mutation Usage")
    lines.append("")
    lines.append("| Operator | Uses |")
    lines.append("|----------|------|")
    for mut, count in mutation_counts.most_common():
        lines.append(f"| {mut} | {count} |")
    lines.append("")

    lines.append("## Cycle History")
    lines.append("")
    lines.append("| Cycle | Score | Benchmark | Mutation | Tests | Test Qual | Hidden | Files | Tokens |")
    lines.append("|-------|-------|-----------|----------|-------|-----------|--------|-------|--------|")
    for e in entries:
        lines.append(
            f"| {e.get('cycle', '?'):>4} "
            f"| {e.get('score', 0):>5.1f} "
            f"| {e.get('benchmark', '?'):12s} "
            f"| {e.get('mutation', '?'):8s} "
            f"| {'Y' if e.get('has_tests') else 'N'} "
            f"| {e.get('test_quality', 0):>5.1f} "
            f"| {'Y' if e.get('hidden_tests_pass') else 'N'} "
            f"| {e.get('files_generated', 0):>3d} "
            f"| {e.get('llm_total_tokens', 0):>5d} "
            f"|"
        )
    lines.append("")

    lines.append("## Metadata")
    lines.append("")
    lines.append(f"- **Generated projects:** `generated_projects/`")
    lines.append(f"- **Archives:** `experiments/projects/`")
    lines.append(f"- **Mutation weights:** `memory/mutation_weights.json`")
    lines.append(f"- **Population:** `population/population.json`")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    """Read the experiment log and write the summary report."""
    entries: list[dict[str, Any]] = load_entries()
    report: str = generate_report(entries)
    print(report)
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(report)


if __name__ == "__main__":
    main()
