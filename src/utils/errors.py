"""Custom exceptions for Solar PV LLM AI"""


class SolarPVAIException(Exception):
    """Base exception for the application"""
    pass


class PineconeIntegrationError(SolarPVAIException):
    """Raised when Pinecone operations fail"""
    pass


class EmbeddingError(SolarPVAIException):
    """Raised when embedding generation fails"""
    pass


class ConfigurationError(SolarPVAIException):
    """Raised when configuration is invalid"""
    pass


class ValidationError(SolarPVAIException):
    """Raised when input validation fails"""
    pass
