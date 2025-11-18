"""End-to-end integration tests"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.api import SolarPVMultiAgent
from src.supervisor.supervisor_agent import SupervisorAgent


class TestEndToEndIntegration:
    """Test complete end-to-end workflows"""

    @pytest.fixture
    def agent_system(self, mock_system_config):
        """Create a complete agent system"""
        return SolarPVMultiAgent(system_config=mock_system_config, log_level="ERROR")

    @pytest.mark.asyncio
    async def test_simple_iec_query(self, agent_system):
        """Test a simple IEC standards query"""
        # This test requires actual API keys to work
        # For testing without API keys, we'll mock the responses

        mock_response = {
            "response": "IEC 61215 is the standard for terrestrial PV module design qualification.",
            "agents_used": ["iec_standards_001"],
            "execution_time": 1.5
        }

        with patch.object(
            agent_system.supervisor,
            'process_query',
            new=AsyncMock(return_value=mock_response)
        ):
            result = await agent_system.query("What is IEC 61215?")

            assert "response" in result
            assert len(result["agents_used"]) > 0
            assert result["execution_time"] >= 0

    @pytest.mark.asyncio
    async def test_multi_agent_collaboration(self, agent_system):
        """Test a query requiring multiple agents"""
        mock_response = {
            "response": "Comprehensive answer from multiple agents",
            "agents_used": ["iec_standards_001", "testing_specialist_001"],
            "execution_time": 2.5
        }

        with patch.object(
            agent_system.supervisor,
            'process_query',
            new=AsyncMock(return_value=mock_response)
        ):
            result = await agent_system.query(
                "What testing is required for IEC compliance?"
            )

            assert len(result["agents_used"]) > 1

    @pytest.mark.asyncio
    async def test_get_capabilities(self, agent_system):
        """Test getting agent capabilities"""
        capabilities = await agent_system.get_capabilities()

        assert "iec_standards_001" in capabilities
        assert "testing_specialist_001" in capabilities
        assert "performance_analyst_001" in capabilities

        # Check structure of capabilities
        for agent_id, cap in capabilities.items():
            assert "agent_type" in cap
            assert "keywords" in cap
            assert "description" in cap

    def test_get_system_info(self, agent_system):
        """Test getting system information"""
        info = agent_system.get_system_info()

        assert "total_agents" in info
        assert info["total_agents"] == 3
        assert "agent_types" in info
        assert len(info["agent_types"]) == 3

    @pytest.mark.asyncio
    async def test_query_specific_agent(self, agent_system):
        """Test querying a specific agent directly"""
        mock_response = AgentResponse(
            agent_id="iec_standards_001",
            agent_type="iec_standards_expert",
            content="Direct response from IEC agent",
            confidence=0.9
        )

        # Import here to avoid circular imports
        from src.core.protocols import AgentResponse

        with patch.object(
            agent_system.supervisor.agents['iec_standards_001'],
            'process',
            new=AsyncMock(return_value=mock_response)
        ):
            result = await agent_system.query_specific_agent(
                "iec_standards_expert",
                "What is IEC 61730?"
            )

            assert result is not None
            assert result["agent_type"] == "iec_standards_expert"
            assert "response" in result


class TestSupervisorAgent:
    """Test SupervisorAgent directly"""

    @pytest.fixture
    def supervisor(self, mock_system_config):
        """Create a supervisor agent"""
        return SupervisorAgent(mock_system_config)

    def test_supervisor_initialization(self, supervisor):
        """Test supervisor initializes with all agents"""
        assert len(supervisor.agents) == 3
        assert "iec_standards_001" in supervisor.agents
        assert "testing_specialist_001" in supervisor.agents
        assert "performance_analyst_001" in supervisor.agents

    def test_get_system_info(self, supervisor):
        """Test getting system info from supervisor"""
        info = supervisor.get_system_info()
        assert info["total_agents"] == 3
        assert len(info["agent_ids"]) == 3
