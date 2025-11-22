# Multi-Agent System Architecture

## Overview

The Solar PV Multi-Agent System is designed with a hierarchical architecture that enables intelligent routing, task decomposition, and collaborative problem-solving for Solar PV related queries.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                      User Interface                      │
│                     (API / Client)                       │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  Supervisor Agent                        │
│  - Query intake                                          │
│  - System coordination                                   │
│  - Response delivery                                     │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Router     │ │ Orchestrator │ │  Synthesizer │
│              │ │              │ │              │
│ - Intent     │ │ - Task       │ │ - Response   │
│   detection  │ │   decompose  │ │   synthesis  │
│ - Agent      │ │ - Coordinate │ │ - Conflict   │
│   selection  │ │   execution  │ │   resolution │
└──────────────┘ └──────────────┘ └──────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│     IEC      │ │   Testing    │ │ Performance  │
│  Standards   │ │  Specialist  │ │   Analyst    │
│    Expert    │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
```

## Core Components

### 1. Supervisor Agent

**Responsibility**: Central coordinator of the multi-agent system

**Key Features**:
- Initializes and manages all specialized agents
- Routes queries to appropriate agents
- Coordinates multi-agent collaboration
- Synthesizes final responses

**Code Location**: `src/supervisor/supervisor_agent.py`

### 2. Query Router

**Responsibility**: Intelligent query analysis and agent selection

**Routing Strategy**:
1. **Keyword Matching**: Analyzes query for domain-specific keywords
2. **LLM-based Routing**: Uses LLM to understand intent and context
3. **Capability Scoring**: Evaluates each agent's ability to handle the query
4. **Hybrid Decision**: Combines multiple signals for final routing

**Routing Outputs**:
- Primary agents (main handlers)
- Secondary agents (consultants)
- Collaboration flag
- Confidence score
- Reasoning

**Code Location**: `src/supervisor/router.py`

### 3. Multi-Agent Orchestrator

**Responsibility**: Coordinates execution of multiple agents

**Execution Modes**:

#### Sequential Execution
- Agents process query one after another
- Early termination on high confidence
- Use case: Simple queries with clear ownership

#### Parallel Execution
- Multiple agents process simultaneously
- Faster response time
- Use case: Independent analyses needed

#### Collaborative Execution
- Agents see and build upon each other's responses
- Two-phase process:
  1. Initial independent responses
  2. Collaborative refinement with context
- Use case: Complex queries requiring multiple perspectives

**Task Decomposition**:
- Breaks complex queries into subtasks
- Assigns subtasks to specialized agents
- Manages execution order (sequential/parallel)

**Code Location**: `src/supervisor/orchestrator.py`

### 4. Specialized Agents

Each agent inherits from `BaseAgent` and implements:

#### IEC Standards Expert
- **Domain**: International Electrotechnical Commission standards
- **Expertise**:
  - IEC 61215 (Module design qualification)
  - IEC 61730 (Module safety)
  - IEC 62446 (Grid connected systems)
  - IEC 61727 (Utility interface)
  - IEC 60364-7-712 (Electrical installations)
- **Keywords**: iec, standard, compliance, certification, regulation
- **Code**: `src/agents/iec_standards_agent.py`

#### Testing Specialist
- **Domain**: PV system testing and quality assurance
- **Expertise**:
  - Module testing (flash, thermal, EL)
  - System commissioning
  - Diagnostic procedures
  - Test equipment and methodology
- **Keywords**: test, inspection, diagnostic, commissioning, quality
- **Code**: `src/agents/testing_specialist_agent.py`

#### Performance Analyst
- **Domain**: System performance and optimization
- **Expertise**:
  - Performance metrics (PR, specific yield)
  - Loss analysis (soiling, shading, thermal)
  - Optimization strategies
  - Degradation analysis
- **Keywords**: performance, efficiency, yield, optimization, losses
- **Code**: `src/agents/performance_analyst_agent.py`

## Communication Protocols

### Message Format

```python
Message(
    role: MessageRole,        # USER, AGENT, SUPERVISOR, SYSTEM
    content: str,             # Message content
    metadata: Dict,           # Additional context
    timestamp: datetime,      # Creation time
    agent_id: Optional[str]   # Sender identifier
)
```

### Agent Response Format

```python
AgentResponse(
    agent_id: str,                    # Agent identifier
    agent_type: str,                  # Agent role/type
    content: str,                     # Response content
    confidence: float,                # 0.0 to 1.0
    reasoning: Optional[str],         # Explanation
    sources: List[str],               # Reference sources
    metadata: Dict,                   # Additional info
    requires_collaboration: bool,     # Multi-agent flag
    suggested_agents: List[str]       # Suggested collaborators
)
```

## Coordination Protocols

### 1. Point-to-Point
- Direct communication between supervisor and single agent
- Use case: Simple, domain-specific queries

### 2. Broadcast
- Supervisor sends query to multiple agents
- Agents respond independently
- Use case: Diverse perspectives needed

### 3. Hierarchical
- Supervisor decomposes task
- Assigns subtasks to agents
- Synthesizes final response
- Use case: Complex, multi-faceted queries

### 4. Collaborative
- Initial independent responses
- Agents review each other's work
- Build upon collective knowledge
- Use case: Queries requiring integrated expertise

## Fallback Mechanisms

### 1. Routing Fallback
- If LLM routing fails → Use keyword-based routing
- If no suitable agent → Route to all with low confidence

### 2. Agent Fallback
- If agent fails → Return error response with confidence 0.0
- Continue with remaining agents

### 3. Orchestration Fallback
- If orchestration fails → Return error message
- Log error for debugging

### 4. Synthesis Fallback
- If synthesis fails → Return best single response
- For single response → Return directly without synthesis

## Performance Optimizations

### 1. Early Termination
- Stop sequential execution on high confidence (>0.8)
- Reduces latency for clear queries

### 2. Parallel Execution
- Execute independent agents simultaneously
- Reduces total latency

### 3. Smart Routing
- Avoid unnecessary agent invocations
- Focus computational resources

### 4. Response Caching
- Can be added for repeated queries
- Reduces API costs

## Extensibility

### Adding New Agents

1. Create agent class inheriting from `BaseAgent`
2. Implement required methods:
   - `capabilities` property
   - `_get_system_prompt()` method
3. Define agent-specific keywords and expertise
4. Register in `SupervisorAgent._initialize_agents()`

### Adding New Coordination Protocols

1. Add protocol definition to `CoordinationProtocol`
2. Implement execution method in `MultiAgentOrchestrator`
3. Update routing logic to select appropriate protocol

## Security & Privacy

- API keys stored in environment variables
- No data persistence by default
- All communication logged for debugging
- Configurable log levels

## Configuration

System behavior controlled via:
- Environment variables (`.env`)
- `SystemConfig` class
- Per-agent `AgentConfig`

Key parameters:
- `default_model`: LLM model for agents
- `supervisor_model`: LLM model for supervisor
- `agent_temperature`: Response creativity (0.0-2.0)
- `max_iterations`: Maximum execution rounds

## Monitoring & Observability

Supported through:
- Structured logging
- Execution time tracking
- Agent confidence scores
- Routing decisions logged
- LangSmith integration (optional)
