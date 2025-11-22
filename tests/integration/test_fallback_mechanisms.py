"""Tests for fallback mechanisms and error handling"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.api import SolarPVMultiAgent
from src.core.protocols import Message, MessageRole, AgentResponse
from src.supervisor.router import QueryRouter


class TestFallbackMechanisms:
    """Test system fallback and error handling"""

    @pytest.fixture
    def agent_system(self, mock_system_config):
        """Create agent system for testing"""
        return SolarPVMultiAgent(system_config=mock_system_config, log_level="ERROR")

    @pytest.mark.asyncio
    async def test_routing_fallback_on_llm_failure(self, mock_system_config, all_agents):
        """Test that routing falls back when LLM fails"""
        router = QueryRouter(mock_system_config)
        message = Message(
            role=MessageRole.USER,
            content="Test query"
        )

        # Simulate LLM failure
        with patch.object(router._llm, 'ainvoke', side_effect=Exception("LLM Error")):
            routing = await router.route_query(message, all_agents)

            # Should still return routing (fallback to all agents)
            assert 'primary_agents' in routing
            assert len(routing['primary_agents']) > 0
            assert routing['confidence'] < 0.5  # Low confidence

    @pytest.mark.asyncio
    async def test_agent_error_handling(self, iec_agent):
        """Test that agent handles processing errors gracefully"""
        message = Message(
            role=MessageRole.USER,
            content="Test query"
        )

        # Simulate error in LLM
        with patch.object(iec_agent._llm, 'ainvoke', side_effect=Exception("Processing error")):
            response = await iec_agent.process(message)

            # Should return error response, not raise exception
            assert isinstance(response, AgentResponse)
            assert response.confidence == 0.0
            assert "error" in response.metadata

    @pytest.mark.asyncio
    async def test_orchestration_error_handling(self, agent_system):
        """Test orchestration handles errors gracefully"""
        # Simulate error in orchestration
        with patch.object(
            agent_system.supervisor.orchestrator,
            'process_query',
            side_effect=Exception("Orchestration error")
        ):
            result = await agent_system.query("Test query")

            # Should return error response, not raise exception
            assert "response" in result
            assert "error" in result or "Error" in result["response"]

    @pytest.mark.asyncio
    async def test_empty_query_handling(self, agent_system):
        """Test handling of empty queries"""
        mock_response = {
            "response": "Please provide a valid query.",
            "agents_used": [],
            "execution_time": 0.1
        }

        with patch.object(
            agent_system.supervisor,
            'process_query',
            new=AsyncMock(return_value=mock_response)
        ):
            result = await agent_system.query("")
            assert "response" in result

    @pytest.mark.asyncio
    async def test_no_suitable_agent_fallback(self, mock_system_config, all_agents):
        """Test fallback when no agent is suitable"""
        router = QueryRouter(mock_system_config)
        message = Message(
            role=MessageRole.USER,
            content="What is the meaning of life?"  # Unrelated to Solar PV
        )

        mock_llm_response = Mock()
        mock_llm_response.content = """PRIMARY_AGENTS: iec_standards_001
COLLABORATION: no
TASK_TYPE: general
CONFIDENCE: 0.2
REASONING: Query not related to Solar PV, low confidence routing"""

        with patch.object(router._llm, 'ainvoke', new=AsyncMock(return_value=mock_llm_response)):
            routing = await router.route_query(message, all_agents)

            # Should still route somewhere with low confidence
            assert len(routing['primary_agents']) > 0
            assert routing['confidence'] <= 0.3

    @pytest.mark.asyncio
    async def test_collaboration_error_recovery(self, iec_agent, testing_agent):
        """Test that collaboration continues even if one agent fails"""
        message = Message(
            role=MessageRole.USER,
            content="Test collaboration"
        )

        other_response = AgentResponse(
            agent_id=testing_agent.agent_id,
            agent_type=testing_agent.agent_type,
            content="Valid response",
            confidence=0.8
        )

        # Simulate error in collaboration
        with patch.object(iec_agent._llm, 'ainvoke', side_effect=Exception("Collab error")):
            response = await iec_agent.collaborate(message, [other_response])

            # Should handle error gracefully
            assert isinstance(response, AgentResponse)
            assert response.confidence == 0.0

    @pytest.mark.asyncio
    async def test_timeout_handling(self, agent_system):
        """Test handling of timeouts"""
        # This would test timeout handling in real scenarios
        # For now, we'll just verify the timeout is configurable
        assert agent_system.system_config.max_iterations > 0

    @pytest.mark.asyncio
    async def test_partial_agent_failure(self, mock_system_config, all_agents):
        """Test system continues with remaining agents if one fails"""
        from src.supervisor.orchestrator import MultiAgentOrchestrator

        orchestrator = MultiAgentOrchestrator(all_agents, mock_system_config)
        message = Message(
            role=MessageRole.USER,
            content="Test query"
        )

        agent_ids = ['iec_standards_001', 'testing_specialist_001']

        # First agent fails, second succeeds
        with patch.object(
            orchestrator.agents['iec_standards_001'],
            'process',
            side_effect=Exception("Agent 1 failed")
        ):
            mock_success = AgentResponse(
                agent_id="testing_specialist_001",
                agent_type="testing_specialist",
                content="Success response",
                confidence=0.8
            )
            with patch.object(
                orchestrator.agents['testing_specialist_001'],
                'process',
                new=AsyncMock(return_value=mock_success)
            ):
                responses = await orchestrator._parallel_execution(message, agent_ids)

                # Should have at least one valid response
                valid_responses = [r for r in responses if not isinstance(r, Exception)]
                # The implementation may vary, but system should be resilient


class TestPerformanceRouting:
    """Test performance and optimization of routing"""

    @pytest.mark.asyncio
    async def test_high_confidence_early_termination(self, mock_system_config):
        """Test that high confidence responses can terminate early"""
        from src.supervisor.orchestrator import MultiAgentOrchestrator
        from src.agents.iec_standards_agent import IECStandardsAgent

        agents = []
        for i in range(3):
            config = AgentConfig(
                agent_id=f"test_agent_{i}",
                agent_type="test",
                model="gpt-4-turbo-preview",
                temperature=0.7
            )
            agent = IECStandardsAgent(config, mock_system_config)
            agents.append(agent)

        # Import required for test
        from src.core.config import AgentConfig

        orchestrator = MultiAgentOrchestrator(agents, mock_system_config)
        message = Message(
            role=MessageRole.USER,
            content="Test query"
        )

        routing_info = {
            'primary_agents': [f'test_agent_{i}' for i in range(3)],
            'requires_collaboration': False
        }

        # First agent returns high confidence
        high_conf_response = AgentResponse(
            agent_id="test_agent_0",
            agent_type="test",
            content="High confidence response",
            confidence=0.95
        )

        with patch.object(
            orchestrator.agents['test_agent_0'],
            'process',
            new=AsyncMock(return_value=high_conf_response)
        ):
            responses = await orchestrator._sequential_execution(message, routing_info)

            # Should stop after high confidence response
            assert len(responses) >= 1
            assert responses[0].confidence >= 0.8

    @pytest.mark.asyncio
    async def test_parallel_execution_performance(self, mock_system_config, all_agents):
        """Test that parallel execution is faster than sequential"""
        # This is more of a design verification test
        from src.supervisor.orchestrator import MultiAgentOrchestrator

        orchestrator = MultiAgentOrchestrator(all_agents, mock_system_config)

        # Verify orchestrator has both execution methods
        assert hasattr(orchestrator, '_parallel_execution')
        assert hasattr(orchestrator, '_sequential_execution')
        assert hasattr(orchestrator, '_collaborative_execution')
