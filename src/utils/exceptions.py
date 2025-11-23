"""Custom exceptions for the multi-agent system"""


class AgentError(Exception):
    """Base exception for agent-related errors"""
    pass


class RoutingError(AgentError):
    """Exception raised when query routing fails"""
    pass


class OrchestrationError(AgentError):
    """Exception raised when orchestration fails"""
    pass


class ConfigurationError(AgentError):
    """Exception raised when configuration is invalid"""
    pass
