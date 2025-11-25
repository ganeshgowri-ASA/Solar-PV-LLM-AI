# API Reference

## Main API Class

### `SolarPVMultiAgent`

Main interface for interacting with the multi-agent system.

```python
from src.api import SolarPVMultiAgent

agent_system = SolarPVMultiAgent(
    system_config: Optional[SystemConfig] = None,
    log_level: str = "INFO"
)
```

#### Parameters

- `system_config` (Optional[SystemConfig]): Custom system configuration. If not provided, loads from environment.
- `log_level` (str): Logging level. Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

#### Methods

##### `async query(question: str, metadata: Optional[Dict] = None) -> Dict`

Submit a query to the multi-agent system.

**Parameters**:
- `question` (str): The question or request to process
- `metadata` (Optional[Dict]): Additional context about the query

**Returns**: Dict containing:
```python
{
    "response": str,              # Final synthesized answer
    "agents_used": List[str],     # Agent IDs that contributed
    "agent_details": List[Dict],  # Detailed info from each agent
    "routing_info": Dict,         # Routing decision information
    "execution_time": float,      # Time in seconds
    "timestamp": datetime         # Processing timestamp
}
```

**Example**:
```python
result = await agent_system.query(
    "What are the IEC 61215 requirements?"
)
print(result['response'])
```

##### `async get_capabilities() -> Dict[str, Any]`

Get information about available agents and their capabilities.

**Returns**: Dict mapping agent IDs to capabilities
```python
{
    "iec_standards_001": {
        "agent_type": str,
        "task_types": List[str],
        "keywords": List[str],
        "description": str,
        "priority": int
    },
    ...
}
```

**Example**:
```python
capabilities = await agent_system.get_capabilities()
for agent_id, cap in capabilities.items():
    print(f"{agent_id}: {cap['description']}")
```

##### `get_system_info() -> Dict[str, Any]`

Get information about the multi-agent system configuration.

**Returns**: Dict with system information
```python
{
    "total_agents": int,
    "agent_types": List[str],
    "agent_ids": List[str],
    "model": str,
    "supervisor_model": str,
    "max_iterations": int
}
```

**Example**:
```python
info = agent_system.get_system_info()
print(f"System has {info['total_agents']} agents")
```

##### `async query_specific_agent(agent_type: str, question: str) -> Optional[Dict]`

Query a specific agent directly, bypassing routing.

**Parameters**:
- `agent_type` (str): Type of agent (iec_standards_expert, testing_specialist, performance_analyst)
- `question` (str): The question to ask

**Returns**: Agent response or None if agent not found
```python
{
    "agent_id": str,
    "agent_type": str,
    "response": str,
    "confidence": float,
    "reasoning": str,
    "metadata": Dict
}
```

**Example**:
```python
result = await agent_system.query_specific_agent(
    "iec_standards_expert",
    "What is IEC 61730?"
)
```

## Configuration Classes

### `SystemConfig`

System-wide configuration loaded from environment variables.

```python
from src.core.config import SystemConfig

config = SystemConfig(
    openai_api_key: Optional[str] = None,
    anthropic_api_key: Optional[str] = None,
    default_llm_provider: str = "openai",
    default_model: str = "gpt-4-turbo-preview",
    supervisor_model: str = "gpt-4-turbo-preview",
    agent_temperature: float = 0.7,
    max_iterations: int = 5,
    log_level: str = "INFO"
)
```

**Environment Variables**:
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `DEFAULT_LLM_PROVIDER`: LLM provider (openai/anthropic)
- `DEFAULT_MODEL`: Model for agents
- `SUPERVISOR_MODEL`: Model for supervisor
- `AGENT_TEMPERATURE`: Response creativity (0.0-2.0)
- `MAX_ITERATIONS`: Maximum execution rounds
- `LOG_LEVEL`: Logging level

### `AgentConfig`

Configuration for individual agents.

```python
from src.core.config import AgentConfig

config = AgentConfig(
    agent_id: str,
    agent_type: str,
    model: str = "gpt-4-turbo-preview",
    temperature: float = 0.7,
    max_tokens: int = 2000,
    timeout: int = 30,
    system_prompt: Optional[str] = None,
    custom_params: Dict[str, Any] = {}
)
```

## Protocol Classes

### `Message`

Message structure for agent communication.

```python
from src.core.protocols import Message, MessageRole

message = Message(
    role: MessageRole,           # USER, AGENT, SUPERVISOR, SYSTEM
    content: str,                # Message content
    metadata: Dict[str, Any] = {},
    timestamp: datetime = now(),
    agent_id: Optional[str] = None
)
```

### `AgentResponse`

Standardized response from agents.

```python
from src.core.protocols import AgentResponse

response = AgentResponse(
    agent_id: str,
    agent_type: str,
    content: str,
    confidence: float,           # 0.0 to 1.0
    reasoning: Optional[str] = None,
    sources: List[str] = [],
    metadata: Dict[str, Any] = {},
    timestamp: datetime = now(),
    requires_collaboration: bool = False,
    suggested_agents: List[str] = []
)
```

### `TaskDecomposition`

Structure for decomposed tasks.

```python
from src.core.protocols import TaskDecomposition

decomposition = TaskDecomposition(
    original_query: str,
    subtasks: List[Dict[str, Any]],
    assigned_agents: List[str],
    execution_order: List[int],
    collaboration_required: bool = False
)
```

## Agent Classes

### `IECStandardsAgent`

Expert in IEC standards for Solar PV systems.

```python
from src.agents.iec_standards_agent import IECStandardsAgent
from src.core.config import AgentConfig, SystemConfig

agent = IECStandardsAgent(
    config: AgentConfig,
    system_config: SystemConfig
)
```

**Capabilities**:
- IEC 61215: Module design qualification
- IEC 61730: Module safety
- IEC 62446: Grid connected systems
- IEC 61727: Utility interface
- IEC 60364-7-712: Electrical installations

### `TestingSpecialistAgent`

Expert in Solar PV system testing.

```python
from src.agents.testing_specialist_agent import TestingSpecialistAgent

agent = TestingSpecialistAgent(
    config: AgentConfig,
    system_config: SystemConfig
)
```

**Capabilities**:
- Module testing (flash, thermal, EL)
- System commissioning
- Diagnostic procedures
- Test equipment selection

### `PerformanceAnalystAgent`

Expert in performance analysis and optimization.

```python
from src.agents.performance_analyst_agent import PerformanceAnalystAgent

agent = PerformanceAnalystAgent(
    config: AgentConfig,
    system_config: SystemConfig
)
```

**Capabilities**:
- Performance metrics (PR, capacity factor)
- Loss analysis
- Optimization strategies
- Degradation analysis

## Supervisor Components

### `SupervisorAgent`

Main coordinator of the multi-agent system.

```python
from src.supervisor.supervisor_agent import SupervisorAgent

supervisor = SupervisorAgent(
    system_config: Optional[SystemConfig] = None
)

# Process query
result = await supervisor.process_query(
    query: str,
    metadata: Optional[Dict] = None
)

# Get capabilities
capabilities = await supervisor.get_agent_capabilities()

# Get system info
info = supervisor.get_system_info()
```

### `QueryRouter`

Intelligent query routing system.

```python
from src.supervisor.router import QueryRouter

router = QueryRouter(system_config: SystemConfig)

routing = await router.route_query(
    message: Message,
    available_agents: List[AgentProtocol]
)
```

**Returns**:
```python
{
    "primary_agents": List[str],
    "secondary_agents": List[str],
    "requires_collaboration": bool,
    "task_type": str,
    "confidence": float,
    "reasoning": str,
    "capability_scores": Dict[str, float]
}
```

### `MultiAgentOrchestrator`

Coordinates multi-agent execution.

```python
from src.supervisor.orchestrator import MultiAgentOrchestrator

orchestrator = MultiAgentOrchestrator(
    agents: List[AgentProtocol],
    system_config: SystemConfig
)

result = await orchestrator.process_query(
    message: Message,
    max_iterations: Optional[int] = None
)
```

## Utility Functions

### `setup_logging`

Configure logging for the application.

```python
from src.utils.logging_config import setup_logging

setup_logging(level: Optional[str] = None)
```

### `create_agent_system`

Convenience function for creating agent system.

```python
from src.api import create_agent_system

agent_system = create_agent_system(
    system_config: Optional[SystemConfig] = None,
    log_level: str = "INFO"
)
```

## Exceptions

### Custom Exceptions

```python
from src.utils.exceptions import (
    AgentError,           # Base exception
    RoutingError,         # Routing failures
    OrchestrationError,   # Orchestration failures
    ConfigurationError    # Configuration issues
)
```

**Usage**:
```python
try:
    result = await agent_system.query("...")
except RoutingError as e:
    print(f"Routing failed: {e}")
except OrchestrationError as e:
    print(f"Orchestration failed: {e}")
```

## Enums

### `TaskType`

Types of tasks handled by agents.

```python
from src.core.protocols import TaskType

TaskType.IEC_STANDARDS
TaskType.TESTING
TaskType.PERFORMANCE
TaskType.GENERAL
TaskType.COLLABORATIVE
```

### `MessageRole`

Roles in agent communication.

```python
from src.core.protocols import MessageRole

MessageRole.USER
MessageRole.AGENT
MessageRole.SUPERVISOR
MessageRole.SYSTEM
```
