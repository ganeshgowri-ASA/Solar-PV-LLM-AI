"""Configuration classes for agents and system"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class AgentConfig(BaseModel):
    """Configuration for individual agents"""
    agent_id: str
    agent_type: str
    model: str = "gpt-4-turbo-preview"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, gt=0)
    timeout: int = Field(default=30, gt=0)
    system_prompt: Optional[str] = None
    custom_params: Dict[str, Any] = Field(default_factory=dict)


class SystemConfig(BaseSettings):
    """System-wide configuration loaded from environment"""
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")

    default_llm_provider: str = Field(default="openai", alias="DEFAULT_LLM_PROVIDER")
    default_model: str = Field(default="gpt-4-turbo-preview", alias="DEFAULT_MODEL")
    supervisor_model: str = Field(default="gpt-4-turbo-preview", alias="SUPERVISOR_MODEL")
    agent_temperature: float = Field(default=0.7, alias="AGENT_TEMPERATURE")
    max_iterations: int = Field(default=5, alias="MAX_ITERATIONS")

    langchain_tracing_v2: bool = Field(default=False, alias="LANGCHAIN_TRACING_V2")
    langchain_api_key: Optional[str] = Field(default=None, alias="LANGCHAIN_API_KEY")
    langchain_project: str = Field(default="solar-pv-multi-agent", alias="LANGCHAIN_PROJECT")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"
