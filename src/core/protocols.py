"""Protocol definitions for multi-agent system"""

from enum import Enum
from typing import Protocol, Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TaskType(str, Enum):
    """Types of tasks that can be handled by agents"""
    IEC_STANDARDS = "iec_standards"
    TESTING = "testing"
    PERFORMANCE = "performance"
    GENERAL = "general"
    COLLABORATIVE = "collaborative"


class MessageRole(str, Enum):
    """Message roles in agent communication"""
    USER = "user"
    AGENT = "agent"
    SUPERVISOR = "supervisor"
    SYSTEM = "system"


class Message(BaseModel):
    """Message structure for agent communication"""
    role: MessageRole
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    agent_id: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AgentResponse(BaseModel):
    """Standardized response from agents"""
    agent_id: str
    agent_type: str
    content: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: Optional[str] = None
    sources: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    requires_collaboration: bool = False
    suggested_agents: List[str] = Field(default_factory=list)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TaskDecomposition(BaseModel):
    """Structure for decomposed tasks"""
    original_query: str
    subtasks: List[Dict[str, Any]]
    assigned_agents: List[str]
    execution_order: List[int]
    collaboration_required: bool = False


class AgentCapability(BaseModel):
    """Definition of agent capabilities"""
    task_types: List[TaskType]
    keywords: List[str]
    description: str
    priority: int = 1


class AgentProtocol(Protocol):
    """Protocol that all agents must implement"""

    @property
    def agent_id(self) -> str:
        """Unique identifier for the agent"""
        ...

    @property
    def agent_type(self) -> str:
        """Type/role of the agent"""
        ...

    @property
    def capabilities(self) -> AgentCapability:
        """Agent's capabilities and specializations"""
        ...

    async def process(self, message: Message) -> AgentResponse:
        """Process a message and return a response"""
        ...

    async def can_handle(self, message: Message) -> float:
        """
        Determine if agent can handle the message
        Returns confidence score between 0.0 and 1.0
        """
        ...

    async def collaborate(
        self,
        message: Message,
        other_responses: List[AgentResponse]
    ) -> AgentResponse:
        """Collaborate with other agents on a task"""
        ...


class CoordinationProtocol(BaseModel):
    """Protocol for multi-agent coordination"""
    coordination_type: str  # sequential, parallel, hierarchical, collaborative
    agents_involved: List[str]
    communication_pattern: str  # broadcast, point-to-point, publish-subscribe
    conflict_resolution: str  # voting, priority-based, supervisor-decision
    timeout_seconds: int = 30
