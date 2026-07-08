"""Tests for the agent spec generator module."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from agent_forge.agent_spec_generator import AgentSpecGenerator


@pytest.fixture
def generator() -> AgentSpecGenerator:
    return AgentSpecGenerator(
        model="test-model",
        base_url="https://test.api/v1",
        api_key="test-key",
        system_prompt="You are a test agent architect.",
    )


class TestAgentSpecGenerator:
    def test_initialization(self, generator: AgentSpecGenerator) -> None:
        assert generator.model == "test-model"
        assert generator.base_url == "https://test.api/v1"
        assert generator.api_key == "test-key"
        assert generator.system_prompt == "You are a test agent architect."

    def test_default_initialization(self) -> None:
        gen = AgentSpecGenerator()
        assert gen.model != ""
        assert gen.base_url != ""
        assert gen.system_prompt != ""

    def test_client_lazy_initialization(self, generator: AgentSpecGenerator) -> None:
        assert generator._client is None
        _ = generator.client
        assert generator._client is not None
        same_client = generator.client
        assert same_client is generator._client

    @pytest.mark.asyncio
    async def test_fallback_spec_structure(self, generator: AgentSpecGenerator) -> None:
        fallback = generator._fallback_spec()
        assert "system_prompt" in fallback
        assert "tools" in fallback
        assert "memory" in fallback
        assert "planning" in fallback
        assert "self_evaluation" in fallback
        assert "output_schema" in fallback
        assert fallback["memory"]["type"] == "conversation_history"
        assert fallback["planning"]["strategy"] == "reAct"

    @pytest.mark.asyncio
    async def test_generate_handles_api_error(self, generator: AgentSpecGenerator) -> None:
        generator._client = MagicMock()
        generator._client.chat = MagicMock()
        generator._client.chat.completions = MagicMock()
        generator._client.chat.completions.create = AsyncMock(
            side_effect=Exception("API Error")
        )

        result = await generator.generate()
        assert result == generator._fallback_spec()

    @pytest.mark.asyncio
    async def test_generate_with_parent_spec(self, generator: AgentSpecGenerator) -> None:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"system_prompt": "evolved", "tools": []}'
        mock_response.usage = MagicMock()
        mock_response.usage.total_tokens = 100

        generator._client = MagicMock()
        generator._client.chat = MagicMock()
        generator._client.chat.completions = MagicMock()
        generator._client.chat.completions.create = AsyncMock(return_value=mock_response)

        parent = {"system_prompt": "old", "tools": ["tool1"]}
        result = await generator.generate(parent_spec=parent)

        assert result == {"system_prompt": "evolved", "tools": []}

    @pytest.mark.asyncio
    async def test_generate_without_parent(self, generator: AgentSpecGenerator) -> None:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"system_prompt": "fresh", "tools": []}'
        mock_response.usage = MagicMock()
        mock_response.usage.total_tokens = 50

        generator._client = MagicMock()
        generator._client.chat = MagicMock()
        generator._client.chat.completions = MagicMock()
        generator._client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await generator.generate()

        assert result == {"system_prompt": "fresh", "tools": []}

    @pytest.mark.asyncio
    async def test_generate_malformed_json_response(
        self, generator: AgentSpecGenerator
    ) -> None:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "not json at all"
        mock_response.usage = MagicMock()
        mock_response.usage.total_tokens = 10

        generator._client = MagicMock()
        generator._client.chat = MagicMock()
        generator._client.chat.completions = MagicMock()
        generator._client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await generator.generate()
        assert result == generator._fallback_spec()

    @pytest.mark.asyncio
    async def test_generate_empty_response(self, generator: AgentSpecGenerator) -> None:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = None
        mock_response.usage = MagicMock()
        mock_response.usage.total_tokens = 0

        generator._client = MagicMock()
        generator._client.chat = MagicMock()
        generator._client.chat.completions = MagicMock()
        generator._client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await generator.generate()
        assert result == {}
