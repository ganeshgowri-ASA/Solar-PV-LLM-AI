"""Multi-agent orchestration and coordination"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from ..core.protocols import (
    Message,
    AgentResponse,
    AgentProtocol,
    TaskDecomposition,
    CoordinationProtocol
)
from ..core.config import SystemConfig
from .router import QueryRouter

logger = logging.getLogger(__name__)


class MultiAgentOrchestrator:
    """
    Orchestrates multiple agents to handle complex queries through
    coordination, collaboration, and task decomposition.
    """

    def __init__(
        self,
        agents: List[AgentProtocol],
        system_config: SystemConfig
    ):
        self.agents = {agent.agent_id: agent for agent in agents}
        self.system_config = system_config
        self.router = QueryRouter(system_config)
        self._llm = ChatOpenAI(
            model=system_config.supervisor_model,
            temperature=0.5,
            api_key=system_config.openai_api_key
        )

    async def process_query(
        self,
        message: Message,
        max_iterations: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process a query through the multi-agent system.

        Returns:
            Dict containing:
                - final_response: Synthesized response from agent(s)
                - agent_responses: Individual agent responses
                - routing_info: Information about routing decisions
                - collaboration_info: Details about agent collaboration
                - execution_time: Time taken to process
        """
        start_time = datetime.now()
        max_iter = max_iterations or self.system_config.max_iterations

        try:
            logger.info(f"Processing query: {message.content[:100]}...")

            # Step 1: Route the query to appropriate agents
            routing_info = await self.router.route_query(
                message,
                list(self.agents.values())
            )

            # Step 2: Check if task decomposition is needed
            if routing_info['requires_collaboration'] and len(routing_info['primary_agents']) > 1:
                task_decomposition = await self._decompose_task(message, routing_info)
            else:
                task_decomposition = None

            # Step 3: Execute based on routing decision
            if routing_info['requires_collaboration']:
                agent_responses = await self._collaborative_execution(
                    message,
                    routing_info,
                    task_decomposition
                )
            else:
                agent_responses = await self._sequential_execution(
                    message,
                    routing_info
                )

            # Step 4: Synthesize final response
            final_response = await self._synthesize_response(
                message,
                agent_responses,
                routing_info
            )

            execution_time = (datetime.now() - start_time).total_seconds()

            return {
                "final_response": final_response,
                "agent_responses": agent_responses,
                "routing_info": routing_info,
                "task_decomposition": task_decomposition,
                "execution_time": execution_time,
                "timestamp": datetime.now()
            }

        except Exception as e:
            logger.error(f"Error in orchestration: {str(e)}")
            return {
                "final_response": f"Error processing query: {str(e)}",
                "agent_responses": [],
                "routing_info": {},
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds()
            }

    async def _decompose_task(
        self,
        message: Message,
        routing_info: Dict[str, Any]
    ) -> TaskDecomposition:
        """Decompose complex task into subtasks for different agents"""

        agents_info = [
            f"- {agent_id}: {self.agents[agent_id].agent_type}"
            for agent_id in routing_info['primary_agents']
            if agent_id in self.agents
        ]

        decomposition_prompt = f"""You are a task decomposition system for a Solar PV multi-agent system.

Original Query: {message.content}

Agents to collaborate:
{chr(10).join(agents_info)}

Decompose this query into specific subtasks that each agent should handle based on their expertise.
Each subtask should be clear, focused, and aligned with an agent's capabilities.

Respond in the following format:
SUBTASK_1: [agent_id] - [specific task for this agent]
SUBTASK_2: [agent_id] - [specific task for this agent]
...
EXECUTION_ORDER: [sequential/parallel]
REASONING: [why this decomposition makes sense]

Example:
SUBTASK_1: iec_standards_001 - Identify applicable IEC standards for module testing
SUBTASK_2: testing_specialist_001 - Describe the testing procedures
EXECUTION_ORDER: sequential
REASONING: Standards must be identified before procedures can be detailed
"""

        messages = [
            SystemMessage(content="You are a task decomposition expert."),
            HumanMessage(content=decomposition_prompt)
        ]

        response = await self._llm.ainvoke(messages)
        return self._parse_task_decomposition(response.content, message.content)

    def _parse_task_decomposition(
        self,
        response: str,
        original_query: str
    ) -> TaskDecomposition:
        """Parse task decomposition response"""
        try:
            lines = response.strip().split('\n')
            subtasks = []
            assigned_agents = []
            execution_order = []
            is_sequential = False

            for i, line in enumerate(lines):
                if line.startswith('SUBTASK_'):
                    # Parse: SUBTASK_X: agent_id - task description
                    parts = line.split(':', 1)[1].strip().split(' - ', 1)
                    if len(parts) == 2:
                        agent_id = parts[0].strip()
                        task_desc = parts[1].strip()
                        subtasks.append({
                            "agent_id": agent_id,
                            "task": task_desc,
                            "order": len(subtasks)
                        })
                        if agent_id not in assigned_agents:
                            assigned_agents.append(agent_id)
                        execution_order.append(len(subtasks) - 1)
                elif line.startswith('EXECUTION_ORDER:'):
                    order = line.split(':', 1)[1].strip().lower()
                    is_sequential = 'sequential' in order

            return TaskDecomposition(
                original_query=original_query,
                subtasks=subtasks,
                assigned_agents=assigned_agents,
                execution_order=execution_order,
                collaboration_required=True
            )

        except Exception as e:
            logger.error(f"Error parsing task decomposition: {str(e)}")
            # Return simple decomposition
            return TaskDecomposition(
                original_query=original_query,
                subtasks=[{"agent_id": "all", "task": original_query, "order": 0}],
                assigned_agents=[],
                execution_order=[0],
                collaboration_required=False
            )

    async def _sequential_execution(
        self,
        message: Message,
        routing_info: Dict[str, Any]
    ) -> List[AgentResponse]:
        """Execute query through agents sequentially"""
        responses = []

        for agent_id in routing_info['primary_agents']:
            if agent_id in self.agents:
                try:
                    agent = self.agents[agent_id]
                    response = await agent.process(message)
                    responses.append(response)

                    # If confidence is high enough, we can stop
                    if response.confidence >= 0.8:
                        logger.info(
                            f"High confidence response from {agent_id}, "
                            f"stopping sequential execution"
                        )
                        break
                except Exception as e:
                    logger.error(f"Error in agent {agent_id}: {str(e)}")

        return responses

    async def _collaborative_execution(
        self,
        message: Message,
        routing_info: Dict[str, Any],
        task_decomposition: Optional[TaskDecomposition] = None
    ) -> List[AgentResponse]:
        """Execute query with agent collaboration"""

        # Phase 1: Get initial responses from all primary agents
        initial_responses = await self._parallel_execution(
            message,
            routing_info['primary_agents']
        )

        # Phase 2: If we have task decomposition, execute subtasks
        if task_decomposition and task_decomposition.subtasks:
            subtask_responses = await self._execute_subtasks(
                message,
                task_decomposition
            )
            initial_responses.extend(subtask_responses)

        # Phase 3: Collaborative round - agents review each other's responses
        collaborative_responses = []
        for agent_id in routing_info['primary_agents']:
            if agent_id in self.agents:
                try:
                    agent = self.agents[agent_id]
                    # Filter out this agent's own response
                    other_responses = [
                        r for r in initial_responses
                        if r.agent_id != agent_id
                    ]
                    if other_responses:
                        collab_response = await agent.collaborate(
                            message,
                            other_responses
                        )
                        collaborative_responses.append(collab_response)
                except Exception as e:
                    logger.error(f"Error in collaboration for {agent_id}: {str(e)}")

        # Return both initial and collaborative responses
        return initial_responses + collaborative_responses

    async def _parallel_execution(
        self,
        message: Message,
        agent_ids: List[str]
    ) -> List[AgentResponse]:
        """Execute query through multiple agents in parallel"""
        tasks = []

        for agent_id in agent_ids:
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                tasks.append(agent.process(message))

        if not tasks:
            return []

        # Execute all agent tasks in parallel
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and log them
        valid_responses = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                logger.error(f"Error in parallel execution: {str(response)}")
            else:
                valid_responses.append(response)

        return valid_responses

    async def _execute_subtasks(
        self,
        message: Message,
        task_decomposition: TaskDecomposition
    ) -> List[AgentResponse]:
        """Execute decomposed subtasks"""
        responses = []

        for subtask in task_decomposition.subtasks:
            agent_id = subtask['agent_id']
            if agent_id in self.agents:
                try:
                    # Create a new message for the subtask
                    subtask_message = Message(
                        role=message.role,
                        content=f"Original query: {message.content}\n\n"
                                f"Your specific task: {subtask['task']}",
                        metadata={**message.metadata, "subtask": True}
                    )

                    agent = self.agents[agent_id]
                    response = await agent.process(subtask_message)
                    responses.append(response)
                except Exception as e:
                    logger.error(f"Error executing subtask for {agent_id}: {str(e)}")

        return responses

    async def _synthesize_response(
        self,
        message: Message,
        agent_responses: List[AgentResponse],
        routing_info: Dict[str, Any]
    ) -> str:
        """Synthesize a final response from multiple agent responses"""

        if not agent_responses:
            return "I apologize, but I couldn't generate a response. Please try again."

        # If only one response, return it directly
        if len(agent_responses) == 1:
            return agent_responses[0].content

        # Multiple responses - synthesize them
        responses_text = []
        for resp in agent_responses:
            responses_text.append(
                f"[{resp.agent_type}] (confidence: {resp.confidence:.2f})\n{resp.content}"
            )

        synthesis_prompt = f"""You are synthesizing responses from multiple specialized agents
for a Solar PV system query.

Original Query: {message.content}

Agent Responses:
{chr(10).join(['---'] + [chr(10).join(['', r, '']) for r in responses_text] + ['---'])}

Create a comprehensive, coherent response that:
1. Integrates insights from all agents
2. Resolves any conflicts or contradictions
3. Provides a clear, actionable answer
4. Maintains technical accuracy
5. Is well-organized and easy to understand

Synthesized Response:"""

        messages = [
            SystemMessage(content="You are a response synthesis expert."),
            HumanMessage(content=synthesis_prompt)
        ]

        response = await self._llm.ainvoke(messages)
        return response.content
