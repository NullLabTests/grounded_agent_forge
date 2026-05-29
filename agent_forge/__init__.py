"""Grounded Agent Forge — evolving full agent blueprints through execution-grounded genetic algorithms.

This module implements the core evolution system for generating and optimizing
autonomous AI agent specifications. The forge evolves complete agent blueprints
including system prompts, tool definitions, memory architectures, planning
strategies, and self-evaluation mechanisms.

Key components:
    - orchestrator: Main evolution loop coordinator
    - agent_spec_generator: Generates agent blueprints via LLM
    - full_agent_evaluator: Multi-objective fitness evaluator (Docker sandbox)
    - meta_evolver: Self-tuning evolution strategy adaptation
"""

from agent_forge.orchestrator import Orchestrator
from agent_forge.agent_spec_generator import AgentSpecGenerator
from agent_forge.full_agent_evaluator import FullAgentEvaluator
from agent_forge.meta_evolver import MetaEvolver

__all__ = [
    "Orchestrator",
    "AgentSpecGenerator",
    "FullAgentEvaluator",
    "MetaEvolver",
]
