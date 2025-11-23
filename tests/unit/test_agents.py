"""Unit tests for individual agents"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.core.protocols import Message, MessageRole, AgentResponse
from src.core.config import AgentConfig


class TestIECStandardsAgent:
    """Test IEC Standards Expert Agent"""

    def test_agent_initialization(self, iec_agent):
        """Test that agent initializes correctly"""
        assert iec_agent.agent_id == "iec_standards_001"
        assert iec_agent.agent_type == "iec_standards_expert"
        assert iec_agent.capabilities is not None

    def test_capabilities(self, iec_agent):
        """Test agent capabilities"""
        cap = iec_agent.capabilities
        assert "iec" in cap.keywords
        assert "standard" in cap.keywords
        assert "compliance" in cap.keywords
        assert len(cap.keywords) > 0

    @pytest.mark.asyncio
    async def test_can_handle_iec_query(self, iec_agent):
        """Test agent can identify IEC-related queries"""
        message = Message(
            role=MessageRole.USER,
            content="What are the IEC 61215 requirements for module testing?"
        )
        score = await iec_agent.can_handle(message)
        assert score > 0.5  # Should have high confidence for IEC query

    @pytest.mark.asyncio
    async def test_can_handle_non_iec_query(self, iec_agent):
        """Test agent gives low score for non-IEC queries"""
        message = Message(
            role=MessageRole.USER,
            content="What is the weather like today?"
        )
        score = await iec_agent.can_handle(message)
        assert score < 0.3  # Should have low confidence


class TestTestingSpecialistAgent:
    """Test Testing Specialist Agent"""

    def test_agent_initialization(self, testing_agent):
        """Test that agent initializes correctly"""
        assert testing_agent.agent_id == "testing_specialist_001"
        assert testing_agent.agent_type == "testing_specialist"

    def test_capabilities(self, testing_agent):
        """Test agent capabilities"""
        cap = testing_agent.capabilities
        assert "test" in cap.keywords
        assert "diagnostic" in cap.keywords
        assert "commissioning" in cap.keywords

    @pytest.mark.asyncio
    async def test_can_handle_testing_query(self, testing_agent):
        """Test agent can identify testing-related queries"""
        message = Message(
            role=MessageRole.USER,
            content="How do I perform flash testing on PV modules?"
        )
        score = await testing_agent.can_handle(message)
        assert score > 0.5


class TestPerformanceAnalystAgent:
    """Test Performance Analyst Agent"""

    def test_agent_initialization(self, performance_agent):
        """Test that agent initializes correctly"""
        assert performance_agent.agent_id == "performance_analyst_001"
        assert performance_agent.agent_type == "performance_analyst"

    def test_capabilities(self, performance_agent):
        """Test agent capabilities"""
        cap = performance_agent.capabilities
        assert "performance" in cap.keywords
        assert "efficiency" in cap.keywords
        assert "optimization" in cap.keywords

    @pytest.mark.asyncio
    async def test_can_handle_performance_query(self, performance_agent):
        """Test agent can identify performance-related queries"""
        message = Message(
            role=MessageRole.USER,
            content="How do I calculate the performance ratio of my PV system?"
        )
        score = await performance_agent.can_handle(message)
        assert score > 0.5


class TestBaseAgentFunctionality:
    """Test common base agent functionality"""

    @pytest.mark.asyncio
    async def test_process_returns_agent_response(self, iec_agent, mock_llm_response):
        """Test that process method returns AgentResponse"""
        message = Message(
            role=MessageRole.USER,
            content="Test query"
        )

        with patch.object(iec_agent._llm, 'ainvoke', new=AsyncMock(return_value=mock_llm_response)):
            response = await iec_agent.process(message)
            assert isinstance(response, AgentResponse)
            assert response.agent_id == iec_agent.agent_id
            assert response.agent_type == iec_agent.agent_type
            assert 0.0 <= response.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_collaborate(self, iec_agent, testing_agent, mock_llm_response):
        """Test collaboration between agents"""
        message = Message(
            role=MessageRole.USER,
            content="What testing is required for IEC compliance?"
        )

        # Create a mock response from testing agent
        other_response = AgentResponse(
            agent_id=testing_agent.agent_id,
            agent_type=testing_agent.agent_type,
            content="Testing procedures include X, Y, Z",
            confidence=0.8
        )

        with patch.object(iec_agent._llm, 'ainvoke', new=AsyncMock(return_value=mock_llm_response)):
            response = await iec_agent.collaborate(message, [other_response])
            assert isinstance(response, AgentResponse)
            assert response.metadata.get('collaboration') is True
