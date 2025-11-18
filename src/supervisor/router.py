"""Intelligent routing for multi-agent system"""

import logging
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from ..core.protocols import Message, TaskType, AgentProtocol
from ..core.config import SystemConfig

logger = logging.getLogger(__name__)


class QueryRouter:
    """
    Intelligent router that analyzes queries and determines which agents
    should handle them based on content, context, and agent capabilities.
    """

    def __init__(self, system_config: SystemConfig):
        self.system_config = system_config
        self._llm = ChatOpenAI(
            model=system_config.supervisor_model,
            temperature=0.3,  # Lower temperature for more consistent routing
            api_key=system_config.openai_api_key
        )

    async def route_query(
        self,
        message: Message,
        available_agents: List[AgentProtocol]
    ) -> Dict[str, Any]:
        """
        Route a query to appropriate agents.

        Returns:
            Dict with:
                - primary_agents: List of agent IDs that should primarily handle the query
                - secondary_agents: List of agent IDs for consultation
                - requires_collaboration: Boolean indicating if multiple agents needed
                - task_type: Identified task type
                - confidence: Routing confidence score
                - reasoning: Explanation of routing decision
        """
        try:
            # First, get capability scores from all agents
            capability_scores = {}
            for agent in available_agents:
                score = await agent.can_handle(message)
                capability_scores[agent.agent_id] = {
                    "score": score,
                    "agent_type": agent.agent_type,
                    "agent": agent
                }

            # Use LLM for intelligent routing decision
            routing_decision = await self._llm_route(message, capability_scores)

            # Combine capability scores with LLM routing
            final_routing = self._combine_routing_decisions(
                capability_scores,
                routing_decision
            )

            logger.info(
                f"Routed query to agents: {final_routing['primary_agents']}, "
                f"collaboration: {final_routing['requires_collaboration']}"
            )

            return final_routing

        except Exception as e:
            logger.error(f"Error in query routing: {str(e)}")
            # Fallback: route to all agents with low confidence
            return {
                "primary_agents": [a.agent_id for a in available_agents],
                "secondary_agents": [],
                "requires_collaboration": True,
                "task_type": TaskType.GENERAL,
                "confidence": 0.3,
                "reasoning": f"Fallback routing due to error: {str(e)}"
            }

    async def _llm_route(
        self,
        message: Message,
        capability_scores: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use LLM to make intelligent routing decision"""

        # Build agent descriptions
        agent_descriptions = []
        for agent_id, info in capability_scores.items():
            agent_descriptions.append(
                f"- {agent_id} ({info['agent_type']}): "
                f"Initial capability score: {info['score']:.2f}"
            )

        routing_prompt = f"""You are a query routing system for a Solar PV multi-agent system.
Analyze the following query and determine which specialized agents should handle it.

Query: {message.content}

Available Agents:
{chr(10).join(agent_descriptions)}

Agent Specializations:
- iec_standards_expert: IEC standards, compliance, certification, regulations
- testing_specialist: Testing procedures, diagnostics, commissioning, quality assurance
- performance_analyst: Performance metrics, optimization, energy yield, loss analysis

Analyze the query and determine:
1. Which agent(s) should primarily handle this query (can be multiple)
2. Whether collaboration between agents is needed
3. The overall task type
4. Confidence in the routing decision (0.0 to 1.0)
5. Brief reasoning for the decision

Respond in the following format:
PRIMARY_AGENTS: [comma-separated list of agent_ids]
COLLABORATION: [yes/no]
TASK_TYPE: [iec_standards/testing/performance/general/collaborative]
CONFIDENCE: [0.0-1.0]
REASONING: [brief explanation]

Consider that:
- Some queries may require multiple agents working together
- Complex queries benefit from collaborative responses
- If unsure, collaboration is preferred
- General queries can be handled by any agent
"""

        messages = [
            SystemMessage(content="You are an intelligent query routing system."),
            HumanMessage(content=routing_prompt)
        ]

        response = await self._llm.ainvoke(messages)
        return self._parse_routing_response(response.content)

    def _parse_routing_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM routing response"""
        try:
            lines = response.strip().split('\n')
            routing = {}

            for line in lines:
                if line.startswith('PRIMARY_AGENTS:'):
                    agents_str = line.split(':', 1)[1].strip()
                    routing['primary_agents'] = [
                        a.strip() for a in agents_str.strip('[]').split(',')
                        if a.strip()
                    ]
                elif line.startswith('COLLABORATION:'):
                    collab = line.split(':', 1)[1].strip().lower()
                    routing['requires_collaboration'] = collab in ['yes', 'true']
                elif line.startswith('TASK_TYPE:'):
                    task = line.split(':', 1)[1].strip()
                    routing['task_type'] = task
                elif line.startswith('CONFIDENCE:'):
                    conf = line.split(':', 1)[1].strip()
                    routing['confidence'] = float(conf)
                elif line.startswith('REASONING:'):
                    reasoning = line.split(':', 1)[1].strip()
                    routing['reasoning'] = reasoning

            return routing

        except Exception as e:
            logger.error(f"Error parsing routing response: {str(e)}")
            return {
                'primary_agents': [],
                'requires_collaboration': True,
                'task_type': TaskType.GENERAL,
                'confidence': 0.3,
                'reasoning': 'Parse error in routing decision'
            }

    def _combine_routing_decisions(
        self,
        capability_scores: Dict[str, Any],
        llm_routing: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine capability scores with LLM routing decision"""

        # Get agents with high capability scores
        high_capability_agents = [
            agent_id for agent_id, info in capability_scores.items()
            if info['score'] >= 0.5
        ]

        # Get primary agents from LLM
        llm_primary = llm_routing.get('primary_agents', [])

        # Combine: prioritize LLM decision but include high-capability agents
        primary_agents = list(set(llm_primary + high_capability_agents))

        # If no primary agents identified, use top scoring agent
        if not primary_agents:
            top_agent = max(
                capability_scores.items(),
                key=lambda x: x[1]['score']
            )[0]
            primary_agents = [top_agent]

        # Secondary agents: medium capability scores not in primary
        secondary_agents = [
            agent_id for agent_id, info in capability_scores.items()
            if 0.3 <= info['score'] < 0.5 and agent_id not in primary_agents
        ]

        return {
            "primary_agents": primary_agents,
            "secondary_agents": secondary_agents,
            "requires_collaboration": (
                llm_routing.get('requires_collaboration', False) or
                len(primary_agents) > 1
            ),
            "task_type": llm_routing.get('task_type', TaskType.GENERAL),
            "confidence": llm_routing.get('confidence', 0.5),
            "reasoning": llm_routing.get('reasoning', 'Combined routing decision'),
            "capability_scores": {
                agent_id: info['score']
                for agent_id, info in capability_scores.items()
            }
        }
