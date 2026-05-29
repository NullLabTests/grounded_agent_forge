"""Main entry point for running the forge as a module.

Usage:
    python -m agent_forge              # Run with default config
    python -m agent_forge --cycles 50  # Run 50 evolution cycles
    python -m agent_forge --help       # Show help
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys

from agent_forge.orchestrator import EvolutionConfig, Orchestrator


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the forge."""
    parser = argparse.ArgumentParser(
        description="Grounded Agent Forge — evolve agent blueprints with genetic algorithms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m agent_forge                    # Infinite evolution
  python -m agent_forge --cycles 50        # 50 evolution cycles
  python -m agent_forge --population 100   # Population of 100
  python -m agent_forge --verbose          # Debug logging
        """,
    )
    parser.add_argument(
        "--cycles", type=int, default=-1,
        help="Number of evolution cycles (-1 = infinite, default: -1)",
    )
    parser.add_argument(
        "--population", type=int, default=50,
        help="Population size (default: 50)",
    )
    parser.add_argument(
        "--tournament", type=int, default=5,
        help="Tournament selection size (default: 5)",
    )
    parser.add_argument(
        "--mutation-rate", type=float, default=0.7,
        help="Mutation rate (default: 0.7)",
    )
    parser.add_argument(
        "--crossover-rate", type=float, default=0.3,
        help="Crossover rate (default: 0.3)",
    )
    parser.add_argument(
        "--parallel", type=int, default=3,
        help="Parallel generations (default: 3)",
    )
    parser.add_argument(
        "--timeout", type=int, default=300,
        help="Sandbox timeout in seconds (default: 300)",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--version", action="store_true",
        help="Show version and exit",
    )
    return parser.parse_args(argv)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the forge."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


def main() -> int:
    """Main entry point. Returns exit code."""
    args = parse_args()

    if args.version:
        print("Grounded Agent Forge v1.0.0")
        return 0

    setup_logging(args.verbose)

    config = EvolutionConfig(
        population_size=args.population,
        tournament_size=args.tournament,
        mutation_rate=args.mutation_rate,
        crossover_rate=args.crossover_rate,
        parallel_generations=args.parallel,
        sandbox_timeout=args.timeout,
        db_url=os.environ.get("FORGE_DB_URL", "sqlite+aiosqlite:///forge_population.db"),
    )

    orchestrator = Orchestrator(config=config)

    try:
        asyncio.run(orchestrator.run(cycles=args.cycles))
    except KeyboardInterrupt:
        print("\nReceived interrupt, shutting down...")
        orchestrator.stop()
    except Exception as exc:
        logging.error("Fatal error: %s", exc)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
