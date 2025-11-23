"""Core protocols and base classes for multi-agent system"""

from .protocols import AgentProtocol, Message, AgentResponse, TaskType
from .base_agent import BaseAgent
from .config import AgentConfig, SystemConfig

__all__ = [
    "AgentProtocol",
    "Message",
    "AgentResponse",
    "TaskType",
    "BaseAgent",
    "AgentConfig",
    "SystemConfig",
]
