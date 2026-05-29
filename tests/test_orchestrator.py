"""Tests for the orchestrator module."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agent_forge.orchestrator import Blueprint, EvolutionConfig, Orchestrator


@pytest.fixture
def mock_generator() -> MagicMock:
    gen = MagicMock()
    gen.generate = AsyncMock(return_value={"system_prompt": "test", "tools": []})
    return gen


@pytest.fixture
def mock_evaluator() -> MagicMock:
    ev = MagicMock()
    ev.evaluate = AsyncMock(return_value={
        "correctness": 80.0,
        "tool_use_accuracy": 70.0,
        "planning_depth": 60.0,
        "code_quality": 90.0,
        "memory_effectiveness": 50.0,
        "self_evaluation": 40.0,
        "efficiency": 85.0,
        "prompt_quality": 30.0,
    })
    return ev


@pytest.fixture
def mock_meta_evolver() -> MagicMock:
    me = MagicMock()
    me.observe_fitness_delta = MagicMock()
    return me


@pytest.fixture
def orchestrator(
    mock_generator: MagicMock,
    mock_evaluator: MagicMock,
    mock_meta_evolver: MagicMock,
) -> Orchestrator:
    config = EvolutionConfig(
        population_size=10,
        tournament_size=3,
        elitism_count=2,
        convergence_window=5,
        convergence_threshold=0.5,
    )
    return Orchestrator(
        config=config,
        spec_generator=mock_generator,
        evaluator=mock_evaluator,
        meta_evolver=mock_meta_evolver,
    )


class TestBlueprint:
    def test_blueprint_creation(self) -> None:
        bp = Blueprint(
            id="test-1",
            generation=0,
            parent_id=None,
            spec={"key": "value"},
            fitness={"correctness": 90.0},
            fitness_total=90.0,
            created_at=1000.0,
        )
        assert bp.id == "test-1"
        assert bp.generation == 0
        assert bp.parent_id is None
        assert bp.spec == {"key": "value"}
        assert bp.fitness["correctness"] == 90.0
        assert bp.fitness_total == 90.0
        assert bp.created_at == 1000.0

    def test_blueprint_defaults(self) -> None:
        bp = Blueprint(id="test-2", generation=1)
        assert bp.parent_id is None
        assert bp.spec == {}
        assert bp.fitness == {}
        assert bp.fitness_total == 0.0
        assert bp.created_at == 0.0

    def test_blueprint_with_parent(self) -> None:
        child = Blueprint(id="child", generation=1, parent_id="parent-1")
        assert child.parent_id == "parent-1"


class TestEvolutionConfig:
    def test_default_config(self) -> None:
        config = EvolutionConfig()
        assert config.population_size == 50
        assert config.tournament_size == 5
        assert config.elitism_count == 3
        assert config.mutation_rate == 0.7
        assert config.crossover_rate == 0.3
        assert config.parallel_generations == 3
        assert config.sandbox_timeout == 300
        assert config.convergence_window == 20
        assert config.convergence_threshold == 0.01

    def test_custom_config(self) -> None:
        config = EvolutionConfig(
            population_size=100,
            tournament_size=10,
            mutation_rate=0.5,
        )
        assert config.population_size == 100
        assert config.tournament_size == 10
        assert config.mutation_rate == 0.5


class TestOrchestrator:
    def test_initialization(self, orchestrator: Orchestrator) -> None:
        assert orchestrator.config.population_size == 10
        assert orchestrator.generation == 0
        assert orchestrator.best_fitness == 0.0
        assert orchestrator.fitness_history == []
        assert orchestrator.running is False
        assert orchestrator.population == []

    def test_select_champion_empty_population(self, orchestrator: Orchestrator) -> None:
        champion = orchestrator._select_champion()
        assert champion is None

    def test_select_champion_with_population(self, orchestrator: Orchestrator) -> None:
        bp1 = Blueprint(id="1", generation=0, fitness_total=50.0)
        bp2 = Blueprint(id="2", generation=0, fitness_total=80.0)
        bp3 = Blueprint(id="3", generation=0, fitness_total=30.0)
        orchestrator.population = [bp1, bp2, bp3]

        champion = orchestrator._select_champion()
        assert champion is not None
        assert champion.id == "2"
        assert champion.fitness_total == 80.0

    @pytest.mark.asyncio
    async def test_generate_blueprint_with_parent(
        self, orchestrator: Orchestrator, mock_generator: MagicMock
    ) -> None:
        parent = Blueprint(id="parent", generation=0, spec={"key": "old"})
        blueprint = await orchestrator._generate_blueprint(parent)

        assert blueprint.generation == 0
        assert blueprint.parent_id == "parent"
        assert blueprint.spec == {"system_prompt": "test", "tools": []}
        mock_generator.generate.assert_called_once_with({"key": "old"})

    @pytest.mark.asyncio
    async def test_generate_blueprint_without_parent(
        self, orchestrator: Orchestrator, mock_generator: MagicMock
    ) -> None:
        blueprint = await orchestrator._generate_blueprint(None)

        assert blueprint.parent_id is None
        assert blueprint.spec == {"system_prompt": "test", "tools": []}
        mock_generator.generate.assert_called_once_with(None)

    @pytest.mark.asyncio
    async def test_evaluate_blueprint(
        self, orchestrator: Orchestrator, mock_evaluator: MagicMock
    ) -> None:
        bp = Blueprint(id="test", generation=0, spec={"key": "value"})
        fitness = await orchestrator._evaluate_blueprint(bp)

        assert fitness["correctness"] == 80.0
        assert fitness["tool_use_accuracy"] == 70.0
        assert fitness["code_quality"] == 90.0
        assert len(fitness) == 8
        mock_evaluator.evaluate.assert_called_once_with({"key": "value"})

    def test_update_population(self, orchestrator: Orchestrator) -> None:
        bp = Blueprint(id="new", generation=0, fitness_total=0.0)
        fitness = {"correctness": 90.0, "tool_use_accuracy": 80.0}

        orchestrator._update_population(bp, fitness)

        assert bp.fitness == fitness
        assert bp.fitness_total == 170.0
        assert len(orchestrator.population) == 1
        assert orchestrator.population[0].id == "new"
        assert orchestrator.best_fitness == 170.0
        assert orchestrator.fitness_history[-1] == 170.0
        assert orchestrator.generation == 1

    def test_update_population_caps_size(self, orchestrator: Orchestrator) -> None:
        for i in range(orchestrator.config.population_size + 5):
            orchestrator.population.append(
                Blueprint(id=str(i), generation=0, fitness_total=float(i))
            )

        bp = Blueprint(id="new", generation=1, fitness_total=999.0)
        orchestrator._update_population(bp, {"test": 999.0})

        assert len(orchestrator.population) == orchestrator.config.population_size

    def test_update_population_tracks_best(self, orchestrator: Orchestrator) -> None:
        orchestrator.population.append(
            Blueprint(id="best", generation=0, fitness_total=200.0)
        )
        orchestrator.best_fitness = 200.0

        bp = Blueprint(id="new_best", generation=1, fitness_total=250.0)
        orchestrator._update_population(bp, {"test": 250.0})

        assert orchestrator.best_fitness == 250.0
        assert orchestrator.fitness_history[-1] == 250.0

    def test_adjust_strategy_calls_meta_evolver(
        self, orchestrator: Orchestrator, mock_meta_evolver: MagicMock
    ) -> None:
        orchestrator.fitness_history = [100.0, 150.0]
        orchestrator._adjust_strategy()
        mock_meta_evolver.observe_fitness_delta.assert_called_once_with(50.0)

    def test_adjust_strategy_skips_without_history(
        self, orchestrator: Orchestrator, mock_meta_evolver: MagicMock
    ) -> None:
        orchestrator.fitness_history = [100.0]
        orchestrator._adjust_strategy()
        mock_meta_evolver.observe_fitness_delta.assert_not_called()

    def test_convergence_not_detected_early(self, orchestrator: Orchestrator) -> None:
        orchestrator.fitness_history = [10.0, 20.0, 30.0]
        assert orchestrator._check_convergence() is False

    def test_convergence_detected(self, orchestrator: Orchestrator) -> None:
        orchestrator.config.convergence_window = 5
        orchestrator.config.convergence_threshold = 1.0
        orchestrator.fitness_history = [50.0, 50.2, 50.1, 50.3, 50.0]
        assert orchestrator._check_convergence() is True

    def test_convergence_not_detected_with_variation(
        self, orchestrator: Orchestrator
    ) -> None:
        orchestrator.config.convergence_window = 5
        orchestrator.config.convergence_threshold = 1.0
        orchestrator.fitness_history = [50.0, 55.0, 52.0, 58.0, 60.0]
        assert orchestrator._check_convergence() is False

    def test_stop_sets_running_false(self, orchestrator: Orchestrator) -> None:
        orchestrator.running = True
        orchestrator.stop()
        assert orchestrator.running is False

    def test_persist_state_creates_json(
        self, orchestrator: Orchestrator, tmp_path: pytest.TempPathFactory
    ) -> None:
        import json

        orchestrator._db_path = tmp_path / "test_state.json"
        orchestrator.generation = 5
        orchestrator.best_fitness = 99.0
        orchestrator.population = [
            Blueprint(id="bp1", generation=5, fitness_total=99.0)
        ]
        orchestrator.fitness_history = [10.0, 50.0, 99.0]

        import asyncio
        asyncio.run(orchestrator._persist_state())

        state_path = tmp_path / "test_state.json"
        assert state_path.exists()
        with open(state_path) as f:
            state = json.load(f)
        assert state["generation"] == 5
        assert state["best_fitness"] == 99.0
        assert state["population_size"] == 1
        assert state["fitness_history"] == [10.0, 50.0, 99.0]

    @pytest.mark.asyncio
    async def test_run_finite_cycles(
        self, orchestrator: Orchestrator, mock_generator: MagicMock
    ) -> None:
        await orchestrator.run(cycles=3)
        assert orchestrator.generation == 3
        assert len(orchestrator.fitness_history) == 3
        assert orchestrator.running is False

    @pytest.mark.asyncio
    async def test_run_with_empty_population(
        self, orchestrator: Orchestrator
    ) -> None:
        await orchestrator.run(cycles=1)
        assert orchestrator.generation == 1
        assert orchestrator.running is False
