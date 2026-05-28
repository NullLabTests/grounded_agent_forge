"""Update README status section with latest evolution metrics.

Designed to be called from infinite_research_loop.py after each cycle.
Updates a small status block at the top of the README without
disturbing the main documentation content.
"""

import re
from pathlib import Path
from datetime import datetime


def beautify(best_score=0, generation=0, population_size=0):
    readme = Path("README.md")
    if not readme.exists():
        return

    content = readme.read_text()

    status_block = (
        f"\n> **Last Evolution Cycle:** {datetime.now(datetime.UTC).isoformat()} UTC  \n"
        f"> **Generation:** {generation}  \n"
        f"> **Best Score:** {best_score}  \n"
        f"> **Population Size:** {population_size}  \n"
    )

    marker_start = "<!-- EVOLUTION_STATUS_START -->"
    marker_end = "<!-- EVOLUTION_STATUS_END -->"
    status_section = (
        f"{marker_start}\n{status_block}\n{marker_end}"
    )

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
    beautify()
