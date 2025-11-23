"""Main supervisor agent for multi-agent system"""

import logging
from typing import List, Dict, Any, Optional

from ..core.protocols import Message, MessageRole, AgentProtocol
from ..core.config import SystemConfig, AgentConfig
from ..agents.iec_standards_agent import IECStandardsAgent
from ..agents.testing_specialist_agent import TestingSpecialistAgent
from ..agents.performance_analyst_agent import PerformanceAnalystAgent
from .orchestrator import MultiAgentOrchestrator

logger = logging.getLogger(__name__)


class SupervisorAgent:
    """
    Main supervisor agent that manages the multi-agent system.
    Handles query intake, routing, orchestration, and response delivery.
    """

    def __init__(self, system_config: Optional[SystemConfig] = None):
        """Initialize the supervisor with all specialized agents"""
        self.system_config = system_config or SystemConfig()
        self.agents = self._initialize_agents()
        self.orchestrator = MultiAgentOrchestrator(
            agents=list(self.agents.values()),
            system_config=self.system_config
        )

        logger.info(
            f"SupervisorAgent initialized with {len(self.agents)} specialized agents"
        )

    def _initialize_agents(self) -> Dict[str, AgentProtocol]:
        """Initialize all specialized agents"""
        agents = {}

        # IEC Standards Expert
        iec_config = AgentConfig(
            agent_id="iec_standards_001",
            agent_type="iec_standards_expert",
            model=self.system_config.default_model,
            temperature=self.system_config.agent_temperature
        )
        agents["iec_standards_001"] = IECStandardsAgent(
            iec_config,
            self.system_config
        )

        # Testing Specialist
        testing_config = AgentConfig(
            agent_id="testing_specialist_001",
            agent_type="testing_specialist",
            model=self.system_config.default_model,
            temperature=self.system_config.agent_temperature
        )
        agents["testing_specialist_001"] = TestingSpecialistAgent(
            testing_config,
            self.system_config
        )

        # Performance Analyst
        performance_config = AgentConfig(
            agent_id="performance_analyst_001",
            agent_type="performance_analyst",
            model=self.system_config.default_model,
            temperature=self.system_config.agent_temperature
        )
        agents["performance_analyst_001"] = PerformanceAnalystAgent(
            performance_config,
            self.system_config
        )

        return agents

    async def process_query(
        self,
        query: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user query through the multi-agent system.

        Args:
            query: The user's question or request
            metadata: Optional metadata about the query

        Returns:
            Dict containing:
                - response: The final synthesized response
                - agents_used: List of agents that contributed
                - routing_info: Information about routing decisions
                - execution_details: Details about execution
        """
        try:
            # Create message
            message = Message(
                role=MessageRole.USER,
                content=query,
                metadata=metadata or {}
            )

            # Process through orchestrator
            result = await self.orchestrator.process_query(message)

            # Extract agent information
            agents_used = list(set(
                resp.agent_id for resp in result.get('agent_responses', [])
            ))

            return {
                "response": result.get('final_response', ''),
                "agents_used": agents_used,
                "agent_details": [
                    {
                        "agent_id": resp.agent_id,
                        "agent_type": resp.agent_type,
                        "confidence": resp.confidence,
                        "reasoning": resp.reasoning
                    }
                    for resp in result.get('agent_responses', [])
                ],
                "routing_info": result.get('routing_info', {}),
                "task_decomposition": result.get('task_decomposition'),
                "execution_time": result.get('execution_time', 0),
                "timestamp": result.get('timestamp')
            }

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "agents_used": [],
                "error": str(e),
                "execution_time": 0
            }

    async def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get information about all available agents and their capabilities"""
        capabilities = {}

        for agent_id, agent in self.agents.items():
            cap = agent.capabilities
            capabilities[agent_id] = {
                "agent_type": agent.agent_type,
                "task_types": [str(t) for t in cap.task_types],
                "keywords": cap.keywords,
                "description": cap.description,
                "priority": cap.priority
            }

        return capabilities

    def get_system_info(self) -> Dict[str, Any]:
        """Get information about the multi-agent system"""
        return {
            "total_agents": len(self.agents),
            "agent_types": list(set(agent.agent_type for agent in self.agents.values())),
            "agent_ids": list(self.agents.keys()),
            "model": self.system_config.default_model,
            "supervisor_model": self.system_config.supervisor_model,
            "max_iterations": self.system_config.max_iterations
        }
