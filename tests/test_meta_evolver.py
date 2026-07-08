"""Tests for the meta evolver module."""

from __future__ import annotations

import os
import tempfile

import pytest

from agent_forge.meta_evolver import MetaEvolver, OperatorStats


@pytest.fixture
def meta_evolver() -> MetaEvolver:
    return MetaEvolver(
        persistence_path=os.path.join(tempfile.gettempdir(), f"test_meta_{os.getpid()}.json"),
        learning_rate=0.1,
        min_weight=0.1,
        max_weight=3.0,
        stagnation_threshold=5,
    )


class TestOperatorStats:
    def test_initialization(self) -> None:
        stats = OperatorStats(name="test_op")
        assert stats.name == "test_op"
        assert stats.weight == 1.0
        assert stats.uses == 0
        assert stats.successes == 0
        assert stats.total_delta == 0.0
        assert stats.avg_delta == 0.0


class TestMetaEvolver:
    def test_initialization(self, meta_evolver: MetaEvolver) -> None:
        assert meta_evolver.learning_rate == 0.1
        assert meta_evolver.min_weight == 0.1
        assert meta_evolver.max_weight == 3.0
        assert meta_evolver.stagnation_threshold == 5
        assert len(meta_evolver.operators) == 9
        assert meta_evolver._fitness_history == []

    def test_operator_names(self, meta_evolver: MetaEvolver) -> None:
        expected = {
            "mutate_system_prompt",
            "mutate_tools",
            "mutate_memory",
            "mutate_planning",
            "mutate_self_eval",
            "crossover_merge",
            "crossover_hybridize",
            "novelty_inject",
            "elite_boost",
        }
        assert set(meta_evolver.operators.keys()) == expected

    def test_select_operator_returns_valid_name(self, meta_evolver: MetaEvolver) -> None:
        for _ in range(100):
            op = meta_evolver.select_operator()
            assert op in meta_evolver.operators

    def test_select_operator_distribution(self, meta_evolver: MetaEvolver) -> None:
        counts: dict[str, int] = {}
        for _ in range(1000):
            op = meta_evolver.select_operator()
            counts[op] = counts.get(op, 0) + 1

        assert len(counts) >= 8

    def test_select_operator_with_zero_weights(self, meta_evolver: MetaEvolver) -> None:
        for op in meta_evolver.operators.values():
            op.weight = 0.0

        for _ in range(50):
            op = meta_evolver.select_operator()
            assert op in meta_evolver.operators

    def test_observe_fitness_delta_positive(self, meta_evolver: MetaEvolver) -> None:
        meta_evolver.observe_fitness_delta(10.0)
        assert len(meta_evolver._fitness_history) == 1
        assert meta_evolver._stagnation_counter == 0

        meta_evolver.observe_fitness_delta(5.0)
        assert len(meta_evolver._fitness_history) == 2
        assert meta_evolver._stagnation_counter == 0

    def test_observe_fitness_delta_negative(self, meta_evolver: MetaEvolver) -> None:
        meta_evolver.observe_fitness_delta(-1.0)
        assert meta_evolver._stagnation_counter == 1

    def test_record_operator_result_positive_delta(
        self, meta_evolver: MetaEvolver
    ) -> None:
        initial_weight = meta_evolver.operators["mutate_system_prompt"].weight
        meta_evolver.record_operator_result("mutate_system_prompt", 15.0)

        stats = meta_evolver.operators["mutate_system_prompt"]
        assert stats.uses == 1
        assert stats.successes == 1
        assert stats.total_delta == 15.0
        assert stats.weight > initial_weight

    def test_record_operator_result_negative_delta(
        self, meta_evolver: MetaEvolver
    ) -> None:
        initial_weight = meta_evolver.operators["mutate_tools"].weight
        meta_evolver.record_operator_result("mutate_tools", -5.0)

        stats = meta_evolver.operators["mutate_tools"]
        assert stats.uses == 1
        assert stats.successes == 0
        assert stats.total_delta == -5.0
        assert stats.weight < initial_weight

    def test_record_operator_weight_clamping(self, meta_evolver: MetaEvolver) -> None:
        op = "mutate_system_prompt"
        meta_evolver.operators[op].weight = meta_evolver.min_weight
        meta_evolver.record_operator_result(op, -100.0)
        assert meta_evolver.operators[op].weight >= meta_evolver.min_weight

        meta_evolver.operators[op].weight = meta_evolver.max_weight
        meta_evolver.record_operator_result(op, 100.0)
        assert meta_evolver.operators[op].weight <= meta_evolver.max_weight

    def test_stagnation_triggers_novelty_boost(self, meta_evolver: MetaEvolver) -> None:
        novelty_weight_before = meta_evolver.operators["novelty_inject"].weight
        hybridize_weight_before = meta_evolver.operators["crossover_hybridize"].weight

        for _ in range(meta_evolver.stagnation_threshold * 2):
            meta_evolver.observe_fitness_delta(-1.0)

        assert meta_evolver.operators["novelty_inject"].weight > novelty_weight_before
        assert meta_evolver.operators["crossover_hybridize"].weight > hybridize_weight_before

    def test_unknown_operator_ignored(self, meta_evolver: MetaEvolver) -> None:
        meta_evolver.record_operator_result("nonexistent_op", 10.0)
        assert len(meta_evolver.operators) == 9

    def test_get_operator_weights(self, meta_evolver: MetaEvolver) -> None:
        weights = meta_evolver.get_operator_weights()
        assert len(weights) == 9
        for name, weight in weights.items():
            assert name in meta_evolver.operators
            assert weight > 0

    def test_get_summary(self, meta_evolver: MetaEvolver) -> None:
        meta_evolver._fitness_history.clear()
        meta_evolver._stagnation_counter = 0
        meta_evolver.record_operator_result("mutate_system_prompt", 10.0)
        meta_evolver.record_operator_result("mutate_tools", -2.0)
        meta_evolver.observe_fitness_delta(5.0)

        summary = meta_evolver.get_summary()
        assert "operators" in summary
        assert summary["stagnation_counter"] == 0
        assert summary["fitness_history_length"] == 1

        ops = summary["operators"]
        assert "mutate_system_prompt" in ops
        assert "mutate_tools" in ops
        assert ops["mutate_system_prompt"]["uses"] == 1
        assert ops["mutate_system_prompt"]["successes"] == 1

    def test_persist_and_load_state(self, meta_evolver: MetaEvolver) -> None:
        meta_evolver._fitness_history.clear()
        meta_evolver.record_operator_result("mutate_system_prompt", 10.0)
        meta_evolver.record_operator_result("mutate_tools", 5.0)
        meta_evolver.observe_fitness_delta(3.0)

        meta_evolver._persist_state()

        loaded = MetaEvolver(persistence_path=str(meta_evolver._path))
        assert loaded.operators["mutate_system_prompt"].uses == 1
        assert loaded.operators["mutate_tools"].uses == 1
        assert len(loaded._fitness_history) == 1

    def test_load_missing_file(self) -> None:
        evolver = MetaEvolver(
            persistence_path="/nonexistent/path/meta.json",
        )
        assert evolver._fitness_history == []
        assert len(evolver.operators) == 9

    def test_persist_creates_parent_dirs(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        deep_path = tmp_path / "nested" / "dirs" / "meta.json"
        evolver = MetaEvolver(persistence_path=str(deep_path))
        evolver.observe_fitness_delta(10.0)
        evolver._persist_state()
        assert deep_path.exists()
