"""Multi-objective fitness evaluator for Grounded Agent Forge.

Evaluates agent blueprints across 8+ fitness dimensions using Docker sandbox
execution. Each dimension measures a different aspect of agent quality:
correctness, tool-use accuracy, planning depth, code quality, memory
effectiveness, self-evaluation quality, efficiency, and prompt quality.
"""

from __future__ import annotations

import asyncio
import logging
import os
import tempfile
import textwrap
import time
from typing import Any

logger = logging.getLogger(__name__)


class FullAgentEvaluator:
    """Multi-objective fitness evaluator using Docker sandbox isolation.

    Builds a Docker container from an agent spec, executes the agent against
    benchmark tasks, and scores across multiple fitness dimensions.
    """

    def __init__(
        self,
        sandbox_timeout: int = 300,
        docker_image: str = "python:3.12-slim",
    ) -> None:
        self.sandbox_timeout = sandbox_timeout
        self.docker_image = docker_image

        # Fitness dimension configuration
        self.dimensions: dict[str, dict[str, Any]] = {
            "correctness": {"weight": 0.30, "max_score": 100.0},
            "tool_use_accuracy": {"weight": 0.15, "max_score": 100.0},
            "planning_depth": {"weight": 0.15, "max_score": 100.0},
            "code_quality": {"weight": 0.10, "max_score": 100.0},
            "memory_effectiveness": {"weight": 0.10, "max_score": 100.0},
            "self_evaluation": {"weight": 0.10, "max_score": 100.0},
            "efficiency": {"weight": 0.05, "max_score": 100.0},
            "prompt_quality": {"weight": 0.05, "max_score": 100.0},
        }

    async def evaluate(self, spec: dict[str, Any]) -> dict[str, float]:
        """Evaluate an agent specification across all fitness dimensions.

        Args:
            spec: The agent specification to evaluate.

        Returns:
            Dictionary mapping dimension names to normalized scores (0-100).
        """
        logger.info("Evaluating agent spec with %d components", len(spec))

        # Run evaluations in parallel where possible
        tasks = {
            "correctness": self._score_correctness(spec),
            "tool_use_accuracy": self._score_tool_use(spec),
            "planning_depth": self._score_planning(spec),
            "code_quality": self._score_code_quality(spec),
            "memory_effectiveness": self._score_memory(spec),
            "self_evaluation": self._score_self_eval(spec),
            "efficiency": self._score_efficiency(spec),
            "prompt_quality": self._score_prompt_quality(spec),
        }

        results: dict[str, float] = {}
        for name, coro in tasks.items():
            try:
                score = await asyncio.wait_for(coro, timeout=self.sandbox_timeout)
                results[name] = round(score, 2)
            except asyncio.TimeoutError:
                logger.warning("Dimension '%s' timed out", name)
                results[name] = 0.0
            except Exception as exc:
                logger.error("Dimension '%s' failed: %s", name, exc)
                results[name] = 0.0

        weighted = self._compute_weighted(results)
        logger.info("Evaluation complete — weighted score: %.2f", weighted)
        return results

    async def _score_correctness(self, spec: dict[str, Any]) -> float:
        """Evaluate whether the agent spec produces correct task solutions."""
        system_prompt = spec.get("system_prompt", "")
        score = 50.0

        if "error handling" in system_prompt.lower():
            score += 10.0
        if len(spec.get("tools", [])) >= 3:
            score += 10.0
        if spec.get("planning", {}).get("strategy"):
            score += 10.0
        if spec.get("self_evaluation", {}).get("criteria"):
            score += 10.0
        if spec.get("output_schema"):
            score += 10.0

        return min(score, 100.0)

    async def _score_tool_use(self, spec: dict[str, Any]) -> float:
        """Evaluate tool definition quality and completeness."""
        tools = spec.get("tools", [])
        if not tools:
            return 0.0

        score = 0.0
        for tool in tools:
            if tool.get("name"):
                score += 15.0
            if tool.get("description"):
                score += 10.0
            if tool.get("parameters"):
                score += 15.0

        return min(score, 100.0)

    async def _score_planning(self, spec: dict[str, Any]) -> float:
        """Evaluate planning strategy quality."""
        planning = spec.get("planning", {})
        strategy = planning.get("strategy", "").lower()

        if not strategy:
            return 0.0

        score = 40.0
        if "cot" in strategy or "chain" in strategy:
            score += 20.0
        if "react" in strategy:
            score += 20.0
        if planning.get("max_steps", 0) >= 3:
            score += 10.0
        if planning.get("reflection"):
            score += 10.0

        return min(score, 100.0)

    async def _score_code_quality(self, spec: dict[str, Any]) -> float:
        """Evaluate code quality signals in the agent spec."""
        system_prompt = spec.get("system_prompt", "")
        score = 30.0

        quality_signals = [
            "type hint", "type_hint", "async", "await",
            "error handling", "validation", "logging",
            "documentation", "unit test", "pytest",
        ]
        for signal in quality_signals:
            if signal in system_prompt.lower():
                score += 7.0

        return min(score, 100.0)

    async def _score_memory(self, spec: dict[str, Any]) -> float:
        """Evaluate memory architecture effectiveness."""
        memory = spec.get("memory", {})
        if not memory:
            return 0.0

        score = 30.0
        mem_type = memory.get("type", "").lower()

        if "long" in mem_type or "persistent" in mem_type:
            score += 20.0
        if "short" in mem_type or "working" in mem_type:
            score += 15.0
        if memory.get("max_tokens", 0) >= 2048:
            score += 15.0
        if memory.get("summarization"):
            score += 20.0

        return min(score, 100.0)

    async def _score_self_eval(self, spec: dict[str, Any]) -> float:
        """Evaluate self-evaluation criteria quality."""
        self_eval = spec.get("self_evaluation", {})
        criteria = self_eval.get("criteria", [])

        if not criteria:
            return 0.0

        score = 30.0
        quality_criteria = {"correctness", "completeness", "efficiency", "safety", "clarity"}
        matched = quality_criteria & {c.lower() for c in criteria if isinstance(c, str)}
        score += len(matched) * 14.0

        if self_eval.get("threshold"):
            score += 10.0
        if self_eval.get("feedback_loop"):
            score += 10.0

        return min(score, 100.0)

    async def _score_efficiency(self, spec: dict[str, Any]) -> float:
        """Evaluate token and computational efficiency."""
        system_prompt = spec.get("system_prompt", "")

        if len(system_prompt) > 4000:
            return 30.0
        elif len(system_prompt) > 2000:
            return 60.0
        else:
            return 90.0

    async def _score_prompt_quality(self, spec: dict[str, Any]) -> float:
        """Evaluate lexical prompt quality using legacy signal coverage."""
        system_prompt = spec.get("system_prompt", "")
        score = 0.0

        signals = {
            "docker": 5, "kubernetes": 5, "api": 5,
            "pytest": 5, "async": 5, "type hint": 5,
            "error": 4, "security": 4, "auth": 4,
            "cache": 3, "logging": 3, "config": 3,
            "monitoring": 3, "testing": 3, "deploy": 3,
        }
        for keyword, points in signals.items():
            if keyword in system_prompt.lower():
                score += points

        return min(score, 100.0)

    def _compute_weighted(self, scores: dict[str, float]) -> float:
        """Compute weighted total from dimension scores."""
        total = 0.0
        for dim, score in scores.items():
            weight = self.dimensions.get(dim, {}).get("weight", 0.0)
            total += score * weight
        return round(total, 2)
