"""Base agent implementation"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage, AIMessage

from .protocols import (
    Message,
    AgentResponse,
    AgentCapability,
    TaskType,
    MessageRole
)
from .config import AgentConfig, SystemConfig

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all specialized agents"""

    def __init__(self, config: AgentConfig, system_config: SystemConfig):
        self.config = config
        self.system_config = system_config
        self._llm = self._initialize_llm()

    def _initialize_llm(self) -> Any:
        """Initialize the LLM based on configuration"""
        provider = self.system_config.default_llm_provider.lower()

        if provider == "openai":
            return ChatOpenAI(
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                api_key=self.system_config.openai_api_key
            )
        elif provider == "anthropic":
            return ChatAnthropic(
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                api_key=self.system_config.anthropic_api_key
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    @property
    def agent_id(self) -> str:
        """Unique identifier for the agent"""
        return self.config.agent_id

    @property
    def agent_type(self) -> str:
        """Type/role of the agent"""
        return self.config.agent_type

    @property
    @abstractmethod
    def capabilities(self) -> AgentCapability:
        """Agent's capabilities - must be implemented by subclasses"""
        pass

    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        pass

    async def process(self, message: Message) -> AgentResponse:
        """Process a message and return a response"""
        try:
            logger.info(f"Agent {self.agent_id} processing message")

            # Prepare messages for LLM
            messages = [
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=message.content)
            ]

            # Get response from LLM
            response = await self._llm.ainvoke(messages)

            # Extract reasoning and confidence
            reasoning, confidence = self._extract_reasoning_and_confidence(
                response.content
            )

            return AgentResponse(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                content=response.content,
                confidence=confidence,
                reasoning=reasoning,
                metadata={
                    "model": self.config.model,
                    "temperature": self.config.temperature
                }
            )

        except Exception as e:
            logger.error(f"Error in agent {self.agent_id}: {str(e)}")
            return AgentResponse(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                content=f"Error processing request: {str(e)}",
                confidence=0.0,
                metadata={"error": str(e)}
            )

    async def can_handle(self, message: Message) -> float:
        """
        Determine if agent can handle the message
        Returns confidence score between 0.0 and 1.0
        """
        # Check if message contains keywords related to this agent's capabilities
        content_lower = message.content.lower()
        keyword_matches = sum(
            1 for keyword in self.capabilities.keywords
            if keyword.lower() in content_lower
        )

        if keyword_matches == 0:
            return 0.1  # Low baseline confidence

        # Calculate confidence based on keyword matches
        max_possible_matches = len(self.capabilities.keywords)
        confidence = min(0.3 + (keyword_matches / max_possible_matches) * 0.7, 1.0)

        return confidence

    async def collaborate(
        self,
        message: Message,
        other_responses: List[AgentResponse]
    ) -> AgentResponse:
        """Collaborate with other agents on a task"""
        try:
            # Build context from other agents' responses
            context = self._build_collaboration_context(other_responses)

            collaboration_prompt = f"""
You are collaborating with other specialized agents to answer this query.

Original Query: {message.content}

Other Agents' Responses:
{context}

Based on your expertise in {self.agent_type} and considering the other agents'
inputs, provide your analysis and contribution to answering the query.
"""

            messages = [
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=collaboration_prompt)
            ]

            response = await self._llm.ainvoke(messages)

            reasoning, confidence = self._extract_reasoning_and_confidence(
                response.content
            )

            return AgentResponse(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                content=response.content,
                confidence=confidence,
                reasoning=reasoning,
                metadata={
                    "collaboration": True,
                    "collaborated_with": [r.agent_id for r in other_responses]
                }
            )

        except Exception as e:
            logger.error(f"Error in collaboration for agent {self.agent_id}: {str(e)}")
            return AgentResponse(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                content=f"Error in collaboration: {str(e)}",
                confidence=0.0,
                metadata={"error": str(e)}
            )

    def _build_collaboration_context(self, responses: List[AgentResponse]) -> str:
        """Build a context string from other agents' responses"""
        context_parts = []
        for resp in responses:
            context_parts.append(
                f"[{resp.agent_type}] (confidence: {resp.confidence:.2f})\n{resp.content}"
            )
        return "\n\n".join(context_parts)

    def _extract_reasoning_and_confidence(self, content: str) -> tuple[str, float]:
        """
        Extract reasoning and confidence from LLM response
        This is a simple implementation - can be enhanced
        """
        # Default confidence based on response length and quality indicators
        confidence = 0.7

        # Check for uncertainty indicators
        uncertainty_words = ["might", "maybe", "possibly", "unclear", "uncertain"]
        if any(word in content.lower() for word in uncertainty_words):
            confidence -= 0.2

        # Check for confidence indicators
        confidence_words = ["definitely", "certainly", "clearly", "confirmed"]
        if any(word in content.lower() for word in confidence_words):
            confidence += 0.1

        confidence = max(0.0, min(1.0, confidence))

        # Extract reasoning (first paragraph or up to 200 chars)
        reasoning = content[:200] + "..." if len(content) > 200 else content

        return reasoning, confidence
