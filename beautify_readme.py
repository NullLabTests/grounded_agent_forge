"""Update README status section with latest evolution metrics.

Called from infinite_research_loop.py after each evolution cycle.
Updates a small status block at the top of the README without
disturbing the main documentation content.
"""

import re
from pathlib import Path
from datetime import datetime, timezone


def beautify(best_score: float = 0, generation: int = 0, population_size: int = 0) -> None:
    """Update the evolution status block in README.md."""
    readme = Path("README.md")
    if not readme.exists():
        return

    content: str = readme.read_text()

    status_block: str = (
        f"\n> **Last Evolution Cycle:** {datetime.now(timezone.utc).isoformat()} UTC  \n"
        f"> **Generation:** {generation}  \n"
        f"> **Best Score:** {best_score}  \n"
        f"> **Population Size:** {population_size}  \n"
    )

    marker_start: str = "<!-- EVOLUTION_STATUS_START -->"
    marker_end: str = "<!-- EVOLUTION_STATUS_END -->"
    status_section: str = f"{marker_start}\n{status_block}\n{marker_end}"

    if marker_start in content and marker_end in content:
        content = re.sub(
            f"{re.escape(marker_start)}.*?{re.escape(marker_end)}",
            status_section,
            content,
            flags=re.DOTALL,
        )
    else:
        content = content.replace(
            "## Overview",
            f"## Current Status\n\n{status_section}\n\n## Overview",
            1,
        )

    readme.write_text(content)


if __name__ == "__main__":
    import json
    pop = Path("population/population.json")
    if pop.exists():
        data = json.loads(pop.read_text())
        if data:
            best = max(float(d.get("score", 0)) for d in data)
            beautify(best_score=best, generation=len(data), population_size=len(data))
        else:
            beautify()
    else:
        import glob
        txt_files = list(Path("population").glob("*.txt"))
        if txt_files:
            beautify(population_size=len(txt_files))
        else:
            beautify()
