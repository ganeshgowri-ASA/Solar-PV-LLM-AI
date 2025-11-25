"""Main API for the Solar PV Multi-Agent System"""

import asyncio
from typing import Optional, Dict, Any
from .core.config import SystemConfig
from .supervisor.supervisor_agent import SupervisorAgent
from .utils.logging_config import setup_logging


class SolarPVMultiAgent:
    """
    Main API class for the Solar PV Multi-Agent System.

    This class provides a simple interface to interact with the multi-agent system
    for Solar PV related queries.

    Example:
        ```python
        from src.api import SolarPVMultiAgent

        # Initialize the system
        agent_system = SolarPVMultiAgent()

        # Query the system
        result = await agent_system.query(
            "What are the IEC standards for PV module testing?"
        )

        print(result['response'])
        ```
    """

    def __init__(
        self,
        system_config: Optional[SystemConfig] = None,
        log_level: str = "INFO"
    ):
        """
        Initialize the Solar PV Multi-Agent System.

        Args:
            system_config: Optional system configuration. If not provided,
                          will load from environment variables.
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        setup_logging(log_level)
        self.system_config = system_config or SystemConfig()
        self.supervisor = SupervisorAgent(self.system_config)

    async def query(
        self,
        question: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Submit a query to the multi-agent system.

        Args:
            question: The question or request to process
            metadata: Optional metadata about the query

        Returns:
            Dict containing:
                - response: The answer from the system
                - agents_used: List of agents that contributed
                - agent_details: Detailed information from each agent
                - routing_info: Information about how the query was routed
                - execution_time: Time taken to process the query
        """
        return await self.supervisor.process_query(question, metadata)

    async def get_capabilities(self) -> Dict[str, Any]:
        """
        Get information about available agents and their capabilities.

        Returns:
            Dict mapping agent IDs to their capabilities
        """
        return await self.supervisor.get_agent_capabilities()

    def get_system_info(self) -> Dict[str, Any]:
        """
        Get information about the multi-agent system configuration.

        Returns:
            Dict with system information including agent count, types, and configuration
        """
        return self.supervisor.get_system_info()

    async def query_specific_agent(
        self,
        agent_type: str,
        question: str
    ) -> Optional[Dict[str, Any]]:
        """
        Query a specific agent directly (bypassing routing).

        Args:
            agent_type: Type of agent (iec_standards_expert, testing_specialist, performance_analyst)
            question: The question to ask

        Returns:
            Agent response or None if agent not found
        """
        from .core.protocols import Message, MessageRole

        # Find agent by type
        agent = None
        for a in self.supervisor.agents.values():
            if a.agent_type == agent_type:
                agent = a
                break

        if not agent:
            return None

        message = Message(
            role=MessageRole.USER,
            content=question
        )

        response = await agent.process(message)

        return {
            "agent_id": response.agent_id,
            "agent_type": response.agent_type,
            "response": response.content,
            "confidence": response.confidence,
            "reasoning": response.reasoning,
            "metadata": response.metadata
        }


# Convenience function for synchronous usage
def create_agent_system(
    system_config: Optional[SystemConfig] = None,
    log_level: str = "INFO"
) -> SolarPVMultiAgent:
    """
    Create an instance of the Solar PV Multi-Agent System.

    Args:
        system_config: Optional system configuration
        log_level: Logging level

    Returns:
        SolarPVMultiAgent instance
    """
    return SolarPVMultiAgent(system_config, log_level)
