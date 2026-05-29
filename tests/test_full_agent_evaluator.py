"""Tests for the full agent evaluator module."""

from __future__ import annotations

import pytest

from agent_forge.full_agent_evaluator import FullAgentEvaluator


@pytest.fixture
def evaluator() -> FullAgentEvaluator:
    return FullAgentEvaluator(sandbox_timeout=30)


@pytest.fixture
def basic_spec() -> dict:
    return {
        "system_prompt": "You are a helpful assistant with error handling and type hints.",
        "tools": [
            {"name": "search", "description": "Search the web", "parameters": {"query": "string"}},
            {"name": "calculate", "description": "Do math", "parameters": {"expr": "string"}},
            {"name": "remember", "description": "Store data", "parameters": {"key": "string", "value": "string"}},
        ],
        "memory": {
            "type": "long_term_and_working",
            "max_tokens": 4096,
            "summarization": True,
        },
        "planning": {
            "strategy": "react_with_reflection",
            "max_steps": 10,
            "reflection": True,
        },
        "self_evaluation": {
            "criteria": ["correctness", "completeness", "efficiency", "safety"],
            "threshold": 0.8,
            "feedback_loop": True,
        },
        "output_schema": {"type": "json"},
    }


class TestFullAgentEvaluator:
    def test_initialization(self, evaluator: FullAgentEvaluator) -> None:
        assert evaluator.sandbox_timeout == 30
        assert evaluator.docker_image == "python:3.12-slim"
        assert len(evaluator.dimensions) == 8
        assert evaluator.dimensions["correctness"]["weight"] == 0.30
        assert evaluator.dimensions["correctness"]["max_score"] == 100.0

    def test_dimension_structure(self, evaluator: FullAgentEvaluator) -> None:
        total_weight = sum(d["weight"] for d in evaluator.dimensions.values())
        assert abs(total_weight - 1.0) < 0.001, f"Total weight {total_weight} != 1.0"

        for name, config in evaluator.dimensions.items():
            assert 0 < config["weight"] <= 1.0, f"{name}: weight out of range"
            assert config["max_score"] > 0, f"{name}: max_score must be positive"

    @pytest.mark.asyncio
    async def test_evaluate_basic_spec(
        self, evaluator: FullAgentEvaluator, basic_spec: dict
    ) -> None:
        scores = await evaluator.evaluate(basic_spec)

        assert len(scores) == 8
        for dim in evaluator.dimensions:
            assert dim in scores
            assert 0 <= scores[dim] <= 100, f"{dim} score {scores[dim]} out of range"

    @pytest.mark.asyncio
    async def test_evaluate_empty_spec(self, evaluator: FullAgentEvaluator) -> None:
        scores = await evaluator.evaluate({})

        assert len(scores) == 8
        assert scores["correctness"] <= 50.0
        assert scores["tool_use_accuracy"] == 0.0
        assert scores["planning_depth"] == 0.0
        assert scores["memory_effectiveness"] == 0.0

    @pytest.mark.asyncio
    async def test_score_correctness(self, evaluator: FullAgentEvaluator) -> None:
        spec = {"system_prompt": "basic", "tools": [], "planning": {}, "self_evaluation": {}, "output_schema": {}}
        score = await evaluator._score_correctness(spec)
        assert 40.0 <= score <= 60.0

        full_spec = {
            "system_prompt": "Handle errors carefully. Async required.",
            "tools": [{"name": "a"}, {"name": "b"}, {"name": "c"}],
            "planning": {"strategy": "cot"},
            "self_evaluation": {"criteria": ["correctness"]},
            "output_schema": {"type": "json"},
        }
        score2 = await evaluator._score_correctness(full_spec)
        assert score2 > score

    @pytest.mark.asyncio
    async def test_score_tool_use(self, evaluator: FullAgentEvaluator) -> None:
        score = await evaluator._score_tool_use({"tools": []})
        assert score == 0.0

        score2 = await evaluator._score_tool_use({
            "tools": [{"name": "search", "description": "desc", "parameters": {"q": "str"}}]
        })
        assert score2 >= 30.0

    @pytest.mark.asyncio
    async def test_score_planning(self, evaluator: FullAgentEvaluator) -> None:
        score = await evaluator._score_planning({"planning": {}})
        assert score == 0.0

        score2 = await evaluator._score_planning({
            "planning": {"strategy": "cot_react", "max_steps": 5, "reflection": True}
        })
        assert score2 >= 80.0

    @pytest.mark.asyncio
    async def test_score_code_quality(self, evaluator: FullAgentEvaluator) -> None:
        score = await evaluator._score_code_quality({"system_prompt": ""})
        assert score == 30.0

        score2 = await evaluator._score_code_quality({
            "system_prompt": "Use type hints, async/await, error handling, and pytest."
        })
        assert score2 > 30.0

    @pytest.mark.asyncio
    async def test_score_memory(self, evaluator: FullAgentEvaluator) -> None:
        score = await evaluator._score_memory({"memory": {}})
        assert score == 0.0

        score2 = await evaluator._score_memory({
            "memory": {"type": "long_term", "max_tokens": 4096, "summarization": True}
        })
        assert score2 >= 70.0

    @pytest.mark.asyncio
    async def test_score_self_eval(self, evaluator: FullAgentEvaluator) -> None:
        score = await evaluator._score_self_eval({"self_evaluation": {}})
        assert score == 0.0

        score2 = await evaluator._score_self_eval({
            "self_evaluation": {
                "criteria": ["correctness", "completeness", "efficiency"],
                "threshold": 0.8,
                "feedback_loop": True,
            }
        })
        assert score2 >= 70.0

    @pytest.mark.asyncio
    async def test_score_efficiency(self, evaluator: FullAgentEvaluator) -> None:
        long_prompt = "x" * 5000
        score_long = await evaluator._score_efficiency({"system_prompt": long_prompt})
        assert score_long == 30.0

        medium_prompt = "x" * 3000
        score_med = await evaluator._score_efficiency({"system_prompt": medium_prompt})
        assert score_med == 60.0

        short_prompt = "x" * 500
        score_short = await evaluator._score_efficiency({"system_prompt": short_prompt})
        assert score_short == 90.0

    @pytest.mark.asyncio
    async def test_score_prompt_quality(self, evaluator: FullAgentEvaluator) -> None:
        score = await evaluator._score_prompt_quality({"system_prompt": ""})
        assert score == 0.0

        score2 = await evaluator._score_prompt_quality({
            "system_prompt": "docker kubernetes api pytest async error security auth cache"
        })
        assert score2 >= 30.0

    def test_compute_weighted(self, evaluator: FullAgentEvaluator) -> None:
        scores = {
            "correctness": 100.0,
            "tool_use_accuracy": 100.0,
            "planning_depth": 100.0,
            "code_quality": 100.0,
            "memory_effectiveness": 100.0,
            "self_evaluation": 100.0,
            "efficiency": 100.0,
            "prompt_quality": 100.0,
        }
        weighted = evaluator._compute_weighted(scores)
        assert abs(weighted - 100.0) < 0.01

    def test_compute_weighted_zero(self, evaluator: FullAgentEvaluator) -> None:
        scores = {dim: 0.0 for dim in evaluator.dimensions}
        weighted = evaluator._compute_weighted(scores)
        assert weighted == 0.0

    @pytest.mark.asyncio
    async def test_evaluate_timeout(
        self, evaluator: FullAgentEvaluator
    ) -> None:
        evaluator.sandbox_timeout = 0.001

        async def slow_score(*args: object) -> float:
            import asyncio
            await asyncio.sleep(10)
            return 100.0

        evaluator._score_correctness = slow_score  # type: ignore[assignment]
        spec = {"system_prompt": "test"}
        scores = await evaluator.evaluate(spec)
        assert scores["correctness"] == 0.0
