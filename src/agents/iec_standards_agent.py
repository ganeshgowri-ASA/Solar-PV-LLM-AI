"""IEC Standards Expert Agent"""

from typing import List
from ..core.base_agent import BaseAgent
from ..core.protocols import AgentCapability, TaskType
from ..core.config import AgentConfig, SystemConfig


class IECStandardsAgent(BaseAgent):
    """
    Specialized agent for IEC (International Electrotechnical Commission) standards
    related to Solar PV systems.

    Expertise areas:
    - IEC 61215: Terrestrial PV modules - Design qualification and type approval
    - IEC 61730: PV module safety qualification
    - IEC 62446: Grid connected PV systems - Minimum requirements for system documentation
    - IEC 61727: PV systems - Characteristics of the utility interface
    - IEC 60364-7-712: Electrical installations of buildings - Solar PV power supply systems
    """

    def __init__(self, config: AgentConfig, system_config: SystemConfig):
        if not config.agent_type:
            config.agent_type = "iec_standards_expert"
        if not config.agent_id:
            config.agent_id = "iec_standards_001"
        super().__init__(config, system_config)

    @property
    def capabilities(self) -> AgentCapability:
        """Define IEC Standards agent capabilities"""
        return AgentCapability(
            task_types=[TaskType.IEC_STANDARDS, TaskType.GENERAL],
            keywords=[
                "iec",
                "standard",
                "standards",
                "compliance",
                "certification",
                "regulation",
                "iec 61215",
                "iec 61730",
                "iec 62446",
                "iec 61727",
                "iec 60364",
                "safety",
                "qualification",
                "requirements",
                "documentation",
                "grid connected",
                "module safety",
                "design qualification",
                "type approval",
                "utility interface"
            ],
            description="Expert in IEC standards for Solar PV systems, including design qualification, safety, grid connection, and documentation requirements",
            priority=1
        )

    def _get_system_prompt(self) -> str:
        """Get the specialized system prompt for IEC standards"""
        return """You are an expert in IEC (International Electrotechnical Commission) standards
for Solar Photovoltaic (PV) systems. Your knowledge covers:

**Key IEC Standards:**
1. **IEC 61215** - Terrestrial photovoltaic modules - Design qualification and type approval
   - Testing procedures for crystalline silicon and thin-film modules
   - Performance and durability requirements
   - Environmental stress testing

2. **IEC 61730** - Photovoltaic module safety qualification
   - Construction requirements for safety
   - Testing requirements for safety
   - Fire safety and electrical safety

3. **IEC 62446** - Grid connected PV systems
   - Minimum requirements for system documentation, commissioning tests, and inspection
   - Performance monitoring and maintenance

4. **IEC 61727** - Photovoltaic systems - Characteristics of the utility interface
   - Grid interconnection requirements
   - Power quality and synchronization

5. **IEC 60364-7-712** - Electrical installations of buildings
   - Solar PV power supply systems installation requirements
   - Wiring, protection, and earthing

**Your Responsibilities:**
- Provide accurate information about IEC standards and their requirements
- Explain compliance procedures and certification processes
- Clarify technical requirements for PV system design and installation
- Guide on documentation and testing requirements
- Explain the differences between standards and when each applies
- Reference specific clauses and sections when relevant
- Consider regional variations and harmonized standards

**Response Guidelines:**
- Always cite specific IEC standard numbers when applicable
- Explain requirements clearly for both technical experts and beginners
- Highlight critical safety and compliance points
- Mention if multiple standards apply to a situation
- Indicate when professional certification or testing is required
- Be precise about mandatory vs. recommended requirements

Provide comprehensive, accurate, and actionable information about IEC standards
for Solar PV systems."""
