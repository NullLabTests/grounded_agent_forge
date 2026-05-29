"""Agent blueprint generator for Grounded Agent Forge.

Generates full agent specifications from evolved blueprints using an LLM.
An agent spec includes system prompts, tool definitions, memory architecture,
planning strategy, and self-evaluation criteria.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_PROMPT = """You are an autonomous agent architect. Generate a complete agent specification
as a JSON object. The spec must include:
- system_prompt: Core identity and behavior instructions
- tools: Array of tool definitions with name, description, and parameters
- memory: Memory architecture configuration
- planning: Planning strategy configuration
- self_evaluation: Criteria for evaluating own outputs
- output_schema: Expected response format

Be specific and detailed. Avoid generic placeholders."""


class AgentSpecGenerator:
    """Generates agent blueprints by querying an LLM.

    Transforms evolved blueprint representations into full agent specifications
    with structured components ready for sandboxed execution.
    """

    def __init__(
        self,
        model: str = "",
        base_url: str = "",
        api_key: str = "",
        system_prompt: str = "",
    ) -> None:
        self.model = model or os.environ.get("LLM_MODEL", "deepseek-chat")
        self.base_url = base_url or os.environ.get("LLM_BASE_URL", "https://api.deepseek.com/v1")
        self.api_key = api_key or os.environ.get("LLM_API_KEY", "")
        self.system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT

        self._client: AsyncOpenAI | None = None

    @property
    def client(self) -> AsyncOpenAI:
        """Lazy-initialized async OpenAI client."""
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
        return self._client

    async def generate(self, parent_spec: dict[str, Any] | None = None) -> dict[str, Any]:
        """Generate an agent specification, optionally building on a parent.

        Args:
            parent_spec: Optional parent blueprint to evolve from.

        Returns:
            A dictionary containing the complete agent specification.
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]

        if parent_spec:
            messages.append({
                "role": "user",
                "content": (
                    "Evolve and improve this agent specification. "
                    "Fix weaknesses, add capabilities, and enhance clarity. "
                    f"Current spec:\n{json.dumps(parent_spec, indent=2)}"
                ),
            })
        else:
            messages.append({
                "role": "user",
                "content": "Generate a complete agent specification for a general-purpose autonomous agent.",
            })

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.8,
                max_tokens=4000,
            )
            content = response.choices[0].message.content or "{}"
            spec = json.loads(content)

            logger.info(
                "Generated agent spec (%d keys, %d tokens)",
                len(spec),
                response.usage.total_tokens if response.usage else 0,
            )
            return spec

        except Exception as exc:
            logger.error("Failed to generate agent spec: %s", exc)
            return self._fallback_spec()

    def _fallback_spec(self) -> dict[str, Any]:
        """Return a minimal fallback spec when LLM generation fails."""
        return {
            "system_prompt": "You are a helpful assistant.",
            "tools": [],
            "memory": {"type": "conversation_history", "max_tokens": 4096},
            "planning": {"strategy": "reAct", "max_steps": 5},
            "self_evaluation": {"criteria": ["correctness", "completeness"]},
            "output_schema": {"type": "text"},
        }
