"""Unit tests for query routing"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.core.protocols import Message, MessageRole
from src.supervisor.router import QueryRouter


class TestQueryRouter:
    """Test QueryRouter functionality"""

    @pytest.fixture
    def router(self, mock_system_config):
        """Create a QueryRouter instance"""
        return QueryRouter(mock_system_config)

    @pytest.mark.asyncio
    async def test_route_iec_query(self, router, all_agents):
        """Test routing an IEC standards query"""
        message = Message(
            role=MessageRole.USER,
            content="What are the IEC 61215 requirements for PV module certification?"
        )

        mock_llm_response = Mock()
        mock_llm_response.content = """PRIMARY_AGENTS: iec_standards_001
COLLABORATION: no
TASK_TYPE: iec_standards
CONFIDENCE: 0.9
REASONING: Query explicitly asks about IEC 61215 standards"""

        with patch.object(router._llm, 'ainvoke', new=AsyncMock(return_value=mock_llm_response)):
            routing = await router.route_query(message, all_agents)

            assert "iec_standards_001" in routing['primary_agents']
            assert routing['confidence'] >= 0.5
            assert 'iec_standards' in routing['task_type']

    @pytest.mark.asyncio
    async def test_route_testing_query(self, router, all_agents):
        """Test routing a testing query"""
        message = Message(
            role=MessageRole.USER,
            content="How do I perform IV curve testing on solar panels?"
        )

        mock_llm_response = Mock()
        mock_llm_response.content = """PRIMARY_AGENTS: testing_specialist_001
COLLABORATION: no
TASK_TYPE: testing
CONFIDENCE: 0.85
REASONING: Query asks about specific testing procedure"""

        with patch.object(router._llm, 'ainvoke', new=AsyncMock(return_value=mock_llm_response)):
            routing = await router.route_query(message, all_agents)

            assert "testing_specialist_001" in routing['primary_agents']

    @pytest.mark.asyncio
    async def test_route_performance_query(self, router, all_agents):
        """Test routing a performance query"""
        message = Message(
            role=MessageRole.USER,
            content="What is the typical performance ratio for solar installations?"
        )

        mock_llm_response = Mock()
        mock_llm_response.content = """PRIMARY_AGENTS: performance_analyst_001
COLLABORATION: no
TASK_TYPE: performance
CONFIDENCE: 0.9
REASONING: Query asks about performance metrics"""

        with patch.object(router._llm, 'ainvoke', new=AsyncMock(return_value=mock_llm_response)):
            routing = await router.route_query(message, all_agents)

            assert "performance_analyst_001" in routing['primary_agents']

    @pytest.mark.asyncio
    async def test_route_collaborative_query(self, router, all_agents):
        """Test routing a query requiring multiple agents"""
        message = Message(
            role=MessageRole.USER,
            content="What IEC standards apply to performance testing of PV modules?"
        )

        mock_llm_response = Mock()
        mock_llm_response.content = """PRIMARY_AGENTS: iec_standards_001, testing_specialist_001
COLLABORATION: yes
TASK_TYPE: collaborative
CONFIDENCE: 0.8
REASONING: Query requires both standards knowledge and testing expertise"""

        with patch.object(router._llm, 'ainvoke', new=AsyncMock(return_value=mock_llm_response)):
            routing = await router.route_query(message, all_agents)

            assert routing['requires_collaboration'] is True
            assert len(routing['primary_agents']) >= 1

    @pytest.mark.asyncio
    async def test_fallback_routing_on_error(self, router, all_agents):
        """Test that routing falls back gracefully on errors"""
        message = Message(
            role=MessageRole.USER,
            content="Test query"
        )

        # Simulate an error in LLM routing
        with patch.object(router._llm, 'ainvoke', side_effect=Exception("Test error")):
            routing = await router.route_query(message, all_agents)

            # Should still return a routing decision (fallback)
            assert 'primary_agents' in routing
            assert len(routing['primary_agents']) > 0
            assert routing['confidence'] < 0.5  # Low confidence for fallback
