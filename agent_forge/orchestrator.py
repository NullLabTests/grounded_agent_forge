"""Main evolution loop coordinator for Grounded Agent Forge.

The orchestrator manages the complete agent evolution cycle:
  - Load/persist agent blueprint population
  - Select champion via tournament selection
  - Apply mutation and crossover operators
  - Schedule parallel agent generation
  - Track fitness and detect convergence
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agent_forge.agent_spec_generator import AgentSpecGenerator
from agent_forge.full_agent_evaluator import FullAgentEvaluator
from agent_forge.meta_evolver import MetaEvolver

logger = logging.getLogger(__name__)


@dataclass
class Blueprint:
    """An individual agent blueprint in the evolution population."""

    id: str
    generation: int
    parent_id: str | None = None
    spec: dict[str, Any] = field(default_factory=dict)
    fitness: dict[str, float] = field(default_factory=dict)
    fitness_total: float = 0.0
    created_at: float = 0.0


@dataclass
class EvolutionConfig:
    """Configuration for the evolution loop."""

    population_size: int = 50
    tournament_size: int = 5
    elitism_count: int = 3
    mutation_rate: float = 0.7
    crossover_rate: float = 0.3
    parallel_generations: int = 3
    db_url: str = ""
    sandbox_timeout: int = 300
    convergence_window: int = 20
    convergence_threshold: float = 0.01


class Orchestrator:
    """Central coordinator for the agent evolution loop.

    Manages the full cycle of loading a population of agent blueprints,
    selecting champions, applying genetic operators, generating new agents,
    evaluating them, and persisting results.
    """

    def __init__(
        self,
        config: EvolutionConfig | None = None,
        spec_generator: AgentSpecGenerator | None = None,
        evaluator: FullAgentEvaluator | None = None,
        meta_evolver: MetaEvolver | None = None,
    ) -> None:
        self.config = config or EvolutionConfig()
        self.spec_generator = spec_generator or AgentSpecGenerator()
        self.evaluator = evaluator or FullAgentEvaluator()
        self.meta_evolver = meta_evolver or MetaEvolver()

        self.population: list[Blueprint] = []
        self.generation: int = 0
        self.best_fitness: float = 0.0
        self.fitness_history: list[float] = []
        self.running: bool = False

        self._db_path = Path(self.config.db_url.replace("sqlite+aiosqlite:///", ""))

    async def run(self, cycles: int = -1) -> None:
        """Run the evolution loop for the specified number of cycles.

        Args:
            cycles: Number of evolution cycles to run. -1 means infinite.
        """
        self.running = True
        cycle_count = 0

        logger.info("Starting evolution loop (cycles=%s)", "infinite" if cycles < 0 else cycles)

        while self.running and (cycles < 0 or cycle_count < cycles):
            cycle_start = time.time()

            champion = self._select_champion()
            blueprint = await self._generate_blueprint(champion)
            fitness = await self._evaluate_blueprint(blueprint)
            self._update_population(blueprint, fitness)
            self._adjust_strategy()
            await self._persist_state()

            cycle_count += 1
            elapsed = time.time() - cycle_start
            logger.info(
                "Cycle %d | Best: %.2f | Time: %.1fs",
                cycle_count, self.best_fitness, elapsed,
            )

            if self._check_convergence():
                logger.info("Convergence detected — triggering novelty exploration")

        self.running = False
        logger.info("Evolution loop completed after %d cycles", cycle_count)

    def _select_champion(self) -> Blueprint | None:
        """Select the best blueprint from the population using tournament selection."""
        if not self.population:
            return None
        tournament = sorted(
            self.population,
            key=lambda b: b.fitness_total,
            reverse=True,
        )
        return tournament[0]

    async def _generate_blueprint(self, parent: Blueprint | None) -> Blueprint:
        """Generate a new agent blueprint, optionally from a parent."""
        spec = await self.spec_generator.generate(parent.spec if parent else None)
        return Blueprint(
            id=f"gen-{self.generation}-{int(time.time())}",
            generation=self.generation,
            parent_id=parent.id if parent else None,
            spec=spec,
            created_at=time.time(),
        )

    async def _evaluate_blueprint(self, blueprint: Blueprint) -> dict[str, float]:
        """Evaluate an agent blueprint across all fitness dimensions."""
        return await self.evaluator.evaluate(blueprint.spec)

    def _update_population(self, blueprint: Blueprint, fitness: dict[str, float]) -> None:
        """Insert the evaluated blueprint into the population."""
        blueprint.fitness = fitness
        blueprint.fitness_total = sum(fitness.values())
        self.population.append(blueprint)
        self.population.sort(key=lambda b: b.fitness_total, reverse=True)
        self.population = self.population[: self.config.population_size]

        if blueprint.fitness_total > self.best_fitness:
            self.best_fitness = blueprint.fitness_total

        self.fitness_history.append(self.best_fitness)
        self.generation += 1

    def _adjust_strategy(self) -> None:
        """Feed fitness deltas to the meta-evolver for strategy adaptation."""
        if len(self.fitness_history) >= 2:
            delta = self.fitness_history[-1] - self.fitness_history[-2]
            self.meta_evolver.observe_fitness_delta(delta)

    def _check_convergence(self) -> bool:
        """Detect if fitness has plateaued."""
        if len(self.fitness_history) < self.config.convergence_window:
            return False
        recent = self.fitness_history[-self.config.convergence_window :]
        return max(recent) - min(recent) < self.config.convergence_threshold

    async def _persist_state(self) -> None:
        """Save evolution state to the database."""
        if not self._db_path or not self._db_path.name:
            return
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "generation": self.generation,
            "best_fitness": self.best_fitness,
            "population_size": len(self.population),
            "fitness_history": self.fitness_history,
        }
        with open(self._db_path.with_suffix(".json"), "w") as f:
            json.dump(state, f, indent=2)

    def stop(self) -> None:
        """Gracefully stop the evolution loop."""
        self.running = False
        logger.info("Stop requested — completing current cycle")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    orchestrator = Orchestrator()
    asyncio.run(orchestrator.run(cycles=10))
