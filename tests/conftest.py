"""Pytest configuration and fixtures"""

import pytest
import os
from unittest.mock import Mock, AsyncMock
from src.core.config import SystemConfig, AgentConfig
from src.agents.iec_standards_agent import IECStandardsAgent
from src.agents.testing_specialist_agent import TestingSpecialistAgent
from src.agents.performance_analyst_agent import PerformanceAnalystAgent


@pytest.fixture
def mock_system_config():
    """Create a mock system configuration"""
    config = SystemConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY", "mock-key"),
        default_llm_provider="openai",
        default_model="gpt-4-turbo-preview",
        supervisor_model="gpt-4-turbo-preview",
        agent_temperature=0.7,
        max_iterations=5,
        log_level="INFO"
    )
    return config


@pytest.fixture
def mock_agent_config():
    """Create a mock agent configuration"""
    return AgentConfig(
        agent_id="test_agent_001",
        agent_type="test_agent",
        model="gpt-4-turbo-preview",
        temperature=0.7,
        max_tokens=2000
    )


@pytest.fixture
def iec_agent(mock_system_config):
    """Create an IEC standards agent for testing"""
    config = AgentConfig(
        agent_id="iec_standards_001",
        agent_type="iec_standards_expert",
        model="gpt-4-turbo-preview",
        temperature=0.7
    )
    return IECStandardsAgent(config, mock_system_config)


@pytest.fixture
def testing_agent(mock_system_config):
    """Create a testing specialist agent for testing"""
    config = AgentConfig(
        agent_id="testing_specialist_001",
        agent_type="testing_specialist",
        model="gpt-4-turbo-preview",
        temperature=0.7
    )
    return TestingSpecialistAgent(config, mock_system_config)


@pytest.fixture
def performance_agent(mock_system_config):
    """Create a performance analyst agent for testing"""
    config = AgentConfig(
        agent_id="performance_analyst_001",
        agent_type="performance_analyst",
        model="gpt-4-turbo-preview",
        temperature=0.7
    )
    return PerformanceAnalystAgent(config, mock_system_config)


@pytest.fixture
def all_agents(iec_agent, testing_agent, performance_agent):
    """Return all agents as a list"""
    return [iec_agent, testing_agent, performance_agent]


@pytest.fixture
def mock_llm_response():
    """Create a mock LLM response"""
    mock = Mock()
    mock.content = "This is a test response from the LLM."
    return mock
