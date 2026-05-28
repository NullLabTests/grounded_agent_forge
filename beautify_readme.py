from pathlib import Path
from datetime import datetime

def beautify(best_score=0, generation=0, population_size=0):
    readme = Path("README.md")
    existing = readme.read_text() if readme.exists() else ""

    sections = existing.split("---")
    header = f"""# Grounded Evolution System

**Last Evolution Cycle:** {datetime.utcnow().isoformat()} UTC
**Generation:** {generation}
**Best Score:** {best_score}
**Population Size:** {population_size}

## Purpose

This system evolves prompts against **real execution-based benchmarks**.

It optimizes:
- Runtime success
- Test pass rates
- Modularity
- Maintainability
- Execution correctness

---
"""
    readme.write_text(header)


if __name__ == "__main__":
    beautify()
