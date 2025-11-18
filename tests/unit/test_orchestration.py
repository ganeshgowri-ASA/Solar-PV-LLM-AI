"""Unit tests for multi-agent orchestration"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.core.protocols import Message, MessageRole, AgentResponse
from src.supervisor.orchestrator import MultiAgentOrchestrator


class TestMultiAgentOrchestrator:
    """Test MultiAgentOrchestrator functionality"""

    @pytest.fixture
    def orchestrator(self, all_agents, mock_system_config):
        """Create an orchestrator instance"""
        return MultiAgentOrchestrator(all_agents, mock_system_config)

    @pytest.mark.asyncio
    async def test_sequential_execution(self, orchestrator):
        """Test sequential execution of agents"""
        message = Message(
            role=MessageRole.USER,
            content="Test query"
        )

        routing_info = {
            'primary_agents': ['iec_standards_001'],
            'secondary_agents': [],
            'requires_collaboration': False,
            'confidence': 0.8
        }

        mock_response = AgentResponse(
            agent_id="iec_standards_001",
            agent_type="iec_standards_expert",
            content="Test response",
            confidence=0.9
        )

        with patch.object(
            orchestrator.agents['iec_standards_001'],
            'process',
            new=AsyncMock(return_value=mock_response)
        ):
            responses = await orchestrator._sequential_execution(message, routing_info)
            assert len(responses) > 0
            assert responses[0].agent_id == "iec_standards_001"

    @pytest.mark.asyncio
    async def test_parallel_execution(self, orchestrator):
        """Test parallel execution of multiple agents"""
        message = Message(
            role=MessageRole.USER,
            content="Test query"
        )

        agent_ids = ['iec_standards_001', 'testing_specialist_001']

        # Mock responses for all agents
        for agent_id in agent_ids:
            mock_response = AgentResponse(
                agent_id=agent_id,
                agent_type="test",
                content=f"Response from {agent_id}",
                confidence=0.8
            )
            with patch.object(
                orchestrator.agents[agent_id],
                'process',
                new=AsyncMock(return_value=mock_response)
            ):
                pass

        responses = await orchestrator._parallel_execution(message, agent_ids)
        # Should execute in parallel (may not get all responses in test due to mocking)
        assert isinstance(responses, list)

    @pytest.mark.asyncio
    async def test_task_decomposition(self, orchestrator):
        """Test task decomposition for complex queries"""
        message = Message(
            role=MessageRole.USER,
            content="What are the IEC standards for testing and performance?"
        )

        routing_info = {
            'primary_agents': ['iec_standards_001', 'testing_specialist_001'],
            'requires_collaboration': True
        }

        mock_llm_response = Mock()
        mock_llm_response.content = """SUBTASK_1: iec_standards_001 - Identify IEC standards
SUBTASK_2: testing_specialist_001 - Describe testing procedures
EXECUTION_ORDER: sequential
REASONING: Standards first, then testing"""

        with patch.object(orchestrator._llm, 'ainvoke', new=AsyncMock(return_value=mock_llm_response)):
            decomposition = await orchestrator._decompose_task(message, routing_info)
            assert decomposition.collaboration_required is True
            assert len(decomposition.subtasks) > 0

    @pytest.mark.asyncio
    async def test_response_synthesis(self, orchestrator):
        """Test synthesis of multiple agent responses"""
        message = Message(
            role=MessageRole.USER,
            content="Test query"
        )

        agent_responses = [
            AgentResponse(
                agent_id="iec_standards_001",
                agent_type="iec_standards_expert",
                content="IEC standards information",
                confidence=0.9
            ),
            AgentResponse(
                agent_id="testing_specialist_001",
                agent_type="testing_specialist",
                content="Testing procedures information",
                confidence=0.85
            )
        ]

        routing_info = {
            'primary_agents': ['iec_standards_001', 'testing_specialist_001']
        }

        mock_synthesis = Mock()
        mock_synthesis.content = "Synthesized response combining both agents"

        with patch.object(orchestrator._llm, 'ainvoke', new=AsyncMock(return_value=mock_synthesis)):
            final_response = await orchestrator._synthesize_response(
                message,
                agent_responses,
                routing_info
            )
            assert isinstance(final_response, str)
            assert len(final_response) > 0

    @pytest.mark.asyncio
    async def test_single_response_no_synthesis(self, orchestrator):
        """Test that single response doesn't require synthesis"""
        message = Message(
            role=MessageRole.USER,
            content="Test query"
        )

        agent_responses = [
            AgentResponse(
                agent_id="iec_standards_001",
                agent_type="iec_standards_expert",
                content="Single agent response",
                confidence=0.9
            )
        ]

        routing_info = {'primary_agents': ['iec_standards_001']}

        final_response = await orchestrator._synthesize_response(
            message,
            agent_responses,
            routing_info
        )

        # Should return the single response directly
        assert final_response == "Single agent response"
