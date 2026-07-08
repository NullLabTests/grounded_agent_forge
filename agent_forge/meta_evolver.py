"""Self-tuning evolution strategy adaptation for Grounded Agent Forge.

The meta-evolver monitors which genetic operators produce the best fitness
improvements and adjusts operator probabilities in real-time. It also detects
population stagnation and introduces novelty-driven exploration.
"""

from __future__ import annotations

import json
import logging
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class OperatorStats:
    """Tracks performance statistics for a genetic operator."""

    name: str
    weight: float = 1.0
    uses: int = 0
    successes: int = 0
    total_delta: float = 0.0
    avg_delta: float = 0.0


class MetaEvolver:
    """Adapts evolution strategy based on observed operator performance.

    Tracks which mutation and crossover operators produce the best fitness
    deltas, adjusts their probabilities accordingly, and detects stagnation
    that requires novelty-driven intervention.
    """

    def __init__(
        self,
        persistence_path: str = "",
        learning_rate: float = 0.1,
        min_weight: float = 0.1,
        max_weight: float = 3.0,
        stagnation_threshold: int = 15,
    ) -> None:
        self.learning_rate = learning_rate
        self.min_weight = min_weight
        self.max_weight = max_weight
        self.stagnation_threshold = stagnation_threshold

        self._path = Path(persistence_path or os.environ.get("FORGE_META_PATH", "memory/meta_state.json"))
        self._fitness_history: list[float] = []
        self._stagnation_counter: int = 0

        self.operators: dict[str, OperatorStats] = {
            "mutate_system_prompt": OperatorStats(name="mutate_system_prompt"),
            "mutate_tools": OperatorStats(name="mutate_tools"),
            "mutate_memory": OperatorStats(name="mutate_memory"),
            "mutate_planning": OperatorStats(name="mutate_planning"),
            "mutate_self_eval": OperatorStats(name="mutate_self_eval"),
            "crossover_merge": OperatorStats(name="crossover_merge"),
            "crossover_hybridize": OperatorStats(name="crossover_hybridize"),
            "novelty_inject": OperatorStats(name="novelty_inject"),
            "elite_boost": OperatorStats(name="elite_boost"),
        }

        self._load_state()

    def select_operator(self) -> str:
        """Select a genetic operator using weighted random selection."""
        names = list(self.operators.keys())
        weights = [self.operators[n].weight for n in names]
        total = sum(weights)
        if total == 0:
            return random.choice(names)
        probabilities = [w / total for w in weights]
        return random.choices(names, weights=probabilities, k=1)[0]

    def observe_fitness_delta(self, delta: float) -> None:
        """Record a fitness delta after an evolution cycle.

        Updates operator weights based on the observed delta. Positive deltas
        up-weight the operator; negative deltas down-weight it.
        """
        self._fitness_history.append(delta)
        self._update_stagnation(delta)

        if len(self._fitness_history) < 2:
            return

        if delta > 0:
            self._stagnation_counter = 0
        elif delta <= 0:
            self._stagnation_counter += 1

        self._persist_state()

    def record_operator_result(self, operator: str, delta: float) -> None:
        """Record the result of using a specific operator.

        Args:
            operator: Name of the operator used.
            delta: Fitness delta resulting from the operator.
        """
        if operator not in self.operators:
            return

        stats = self.operators[operator]
        stats.uses += 1
        stats.total_delta += delta

        if delta > 0:
            stats.successes += 1

        stats.avg_delta = stats.total_delta / stats.uses if stats.uses > 0 else 0.0

        weight_adjustment = 1.0 + (self.learning_rate * delta / max(abs(delta), 0.01))
        stats.weight = max(self.min_weight, min(self.max_weight, stats.weight * weight_adjustment))

        logger.debug(
            "Operator '%s': delta=%.2f, weight=%.2f, success_rate=%.2f",
            operator, delta, stats.weight,
            stats.successes / stats.uses if stats.uses > 0 else 0.0,
        )

    def _update_stagnation(self, delta: float) -> None:
        """Detect and respond to fitness stagnation."""
        if self._stagnation_counter >= self.stagnation_threshold:
            logger.info("Stagnation detected (%d cycles without improvement)", self._stagnation_counter)
            self._boost_novelty_operators()
            self._stagnation_counter = 0

    def _boost_novelty_operators(self) -> None:
        """Temporarily boost novelty and exploration operator weights."""
        for name in ("novelty_inject", "crossover_hybridize"):
            if name in self.operators:
                self.operators[name].weight = min(
                    self.max_weight,
                    self.operators[name].weight * 2.0,
                )
                logger.info("Boosted '%s' weight to %.2f", name, self.operators[name].weight)

        for name in ("mutate_system_prompt", "mutate_tools"):
            if name in self.operators:
                self.operators[name].weight = max(
                    self.min_weight,
                    self.operators[name].weight * 0.5,
                )

    def get_operator_weights(self) -> dict[str, float]:
        """Return current operator weights for inspection."""
        return {n: s.weight for n, s in self.operators.items()}

    def get_summary(self) -> dict[str, Any]:
        """Return a summary of meta-evolution state."""
        return {
            "operators": {
                name: {
                    "weight": stats.weight,
                    "uses": stats.uses,
                    "successes": stats.successes,
                    "avg_delta": round(stats.avg_delta, 4),
                    "success_rate": round(stats.successes / stats.uses, 4) if stats.uses > 0 else 0.0,
                }
                for name, stats in self.operators.items()
            },
            "stagnation_counter": self._stagnation_counter,
            "fitness_history_length": len(self._fitness_history),
        }

    def _load_state(self) -> None:
        """Load persisted meta-evolution state from disk."""
        try:
            if self._path.exists():
                with open(self._path) as f:
                    state = json.load(f)
                for name, data in state.get("operators", {}).items():
                    if name in self.operators:
                        self.operators[name].weight = data.get("weight", 1.0)
                        self.operators[name].uses = data.get("uses", 0)
                        self.operators[name].successes = data.get("successes", 0)
                        self.operators[name].total_delta = data.get("total_delta", 0.0)
                        self.operators[name].avg_delta = data.get("avg_delta", 0.0)
                self._stagnation_counter = state.get("stagnation_counter", 0)
                self._fitness_history = state.get("fitness_history", [])
                logger.info("Loaded meta-evolution state from %s", self._path)
        except Exception as exc:
            logger.warning("Failed to load meta-evolution state: %s", exc)

    def _persist_state(self) -> None:
        """Persist meta-evolution state to disk."""
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            state = self.get_summary()
            state["fitness_history"] = self._fitness_history
            state["stagnation_counter"] = self._stagnation_counter
            with open(self._path, "w") as f:
                json.dump(state, f, indent=2)
        except Exception as exc:
            logger.warning("Failed to persist meta-evolution state: %s", exc)
