"""LLM Service for Solar PV AI Assistant."""

import os
import uuid
from typing import Optional, List, AsyncGenerator
from ..models.schemas import ExpertiseLevel, Citation


class LLMService:
    """Service for interacting with LLM for Solar PV questions."""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        self.conversations: dict = {}

    def _get_system_prompt(self, expertise_level: ExpertiseLevel) -> str:
        """Get system prompt based on expertise level."""
        base_prompt = """You are an expert Solar PV (Photovoltaic) AI assistant with deep knowledge of:
- Solar panel technology and specifications
- Installation standards and best practices (IEC, NEC, IEEE)
- System design and sizing
- Inverters, batteries, and balance of system components
- Grid-tied and off-grid systems
- Performance monitoring and maintenance
- Safety regulations and compliance
- Economic analysis (ROI, payback periods, LCOE)

Always provide accurate, helpful information with citations when available."""

        level_prompts = {
            ExpertiseLevel.BEGINNER: """
Explain concepts in simple terms, avoiding jargon. Use analogies and examples.
Break down complex topics into easy-to-understand steps.
Assume no prior knowledge of solar PV systems.""",

            ExpertiseLevel.INTERMEDIATE: """
Use standard industry terminology with brief explanations when needed.
Provide practical details and real-world considerations.
Assume basic understanding of solar PV concepts.""",

            ExpertiseLevel.EXPERT: """
Use technical terminology freely and provide detailed technical specifications.
Include relevant standards, equations, and advanced considerations.
Assume comprehensive knowledge of solar PV systems."""
        }

        return base_prompt + level_prompts.get(expertise_level, level_prompts[ExpertiseLevel.INTERMEDIATE])

    def _generate_mock_response(
        self,
        query: str,
        expertise_level: ExpertiseLevel,
        include_citations: bool
    ) -> tuple[str, List[Citation], List[str]]:
        """Generate a mock response for demo purposes."""

        # Mock responses based on query keywords
        query_lower = query.lower()

        if "size" in query_lower or "sizing" in query_lower:
            response = self._get_sizing_response(expertise_level)
            citations = [
                Citation(
                    source="IEC 61724-1:2021",
                    section="5.2",
                    text="System sizing shall account for expected energy yield and performance ratio",
                    relevance_score=0.92
                )
            ] if include_citations else []
            follow_ups = [
                "What factors affect solar panel efficiency?",
                "How do I calculate battery storage needs?",
                "What inverter size do I need?"
            ]
        elif "install" in query_lower:
            response = self._get_installation_response(expertise_level)
            citations = [
                Citation(
                    source="NEC Article 690",
                    section="690.12",
                    text="Rapid shutdown requirements for PV systems on buildings",
                    relevance_score=0.95
                )
            ] if include_citations else []
            follow_ups = [
                "What are the mounting options?",
                "How do I handle roof penetrations?",
                "What permits are required?"
            ]
        elif "efficiency" in query_lower:
            response = self._get_efficiency_response(expertise_level)
            citations = [
                Citation(
                    source="IEC 61853-1:2011",
                    section="4.1",
                    text="Photovoltaic module performance testing under standard test conditions",
                    relevance_score=0.88
                )
            ] if include_citations else []
            follow_ups = [
                "How does temperature affect panel efficiency?",
                "What are half-cut cells?",
                "Compare monocrystalline vs polycrystalline"
            ]
        else:
            response = self._get_general_response(query, expertise_level)
            citations = []
            follow_ups = [
                "How do I size a solar system?",
                "What are the installation requirements?",
                "How do I maximize efficiency?"
            ]

        return response, citations, follow_ups

    def _get_sizing_response(self, level: ExpertiseLevel) -> str:
        responses = {
            ExpertiseLevel.BEGINNER: """To figure out what size solar system you need, think about how much electricity you use.

**Simple steps:**
1. Look at your electricity bills - find your monthly kWh usage
2. A typical home uses 900-1000 kWh/month
3. In most areas, a 1kW solar system produces about 4-5 kWh per day
4. Divide your daily usage by 4-5 to get your system size in kW

**Example:** If you use 900 kWh/month (30 kWh/day), you'd need about a 6-7 kW system.

Think of it like this: each solar panel is like a mini power plant on your roof, and you need enough of them to "grow" all the electricity your home needs!""",

            ExpertiseLevel.INTERMEDIATE: """System sizing involves balancing energy consumption with expected solar production.

**Key factors:**
- **Annual energy consumption:** Review 12 months of utility bills
- **Peak sun hours:** Varies by location (4-6 hours typical in US)
- **System losses:** Account for ~15-20% (inverter efficiency, wiring, soiling)
- **Performance ratio:** Typically 0.75-0.85

**Calculation:**
```
System Size (kW) = Annual kWh / (Peak Sun Hours × 365 × Performance Ratio)
```

**Example:** 10,000 kWh/year ÷ (5 hrs × 365 × 0.80) = 6.85 kW system

Consider roof space constraints and future energy needs when finalizing size.""",

            ExpertiseLevel.EXPERT: """System sizing requires comprehensive analysis of load profiles, resource assessment, and technical constraints.

**Methodology:**
1. **Load Analysis:** Hourly load profiling (8760 analysis preferred)
2. **Resource Assessment:** TMY3/NSRDB data, POA irradiance modeling
3. **System Losses:** Use PVWatts or SAM for detailed loss modeling:
   - Soiling: 2-5%
   - Shading: Site-specific (use shade analysis tools)
   - DC/AC ratio optimization: Typically 1.1-1.3
   - Module mismatch: 2%
   - Wiring losses: 2%
   - Inverter efficiency: 96-98%

**Design considerations:**
- NEC 690 rapid shutdown compliance
- String sizing based on Voc temperature coefficients
- Utility interconnection limits (Rule 21, IEEE 1547)
- Energy storage integration (if applicable)

**Performance modeling:**
Use hourly simulation with performance models per IEC 61853-1 for accurate yield prediction."""
        }
        return responses.get(level, responses[ExpertiseLevel.INTERMEDIATE])

    def _get_installation_response(self, level: ExpertiseLevel) -> str:
        return """Solar panel installation involves several key steps and safety considerations.

**General process:**
1. Site assessment and design
2. Permitting and utility interconnection application
3. Mounting system installation
4. Panel mounting and wiring
5. Inverter and electrical connections
6. Inspection and commissioning

**Important standards:**
- NEC Article 690 - Solar Photovoltaic Systems
- IEC 62446 - Grid connected PV systems
- Local building codes

Always work with licensed installers and obtain proper permits."""

    def _get_efficiency_response(self, level: ExpertiseLevel) -> str:
        return """Solar panel efficiency refers to how much sunlight is converted to electricity.

**Current efficiency ranges:**
- Monocrystalline: 18-22%
- Polycrystalline: 15-18%
- Thin-film: 10-13%
- Premium panels (SunPower, LG): 20-22%+

**Factors affecting efficiency:**
- Temperature (efficiency decreases ~0.3-0.5% per °C above 25°C)
- Shading
- Orientation and tilt angle
- Soiling and maintenance
- Age degradation (~0.5% per year)

Higher efficiency panels cost more but require less roof space."""

    def _get_general_response(self, query: str, level: ExpertiseLevel) -> str:
        return f"""Thank you for your question about solar PV systems.

Solar photovoltaic technology converts sunlight directly into electricity using semiconductor materials. Modern solar systems are highly reliable with 25+ year warranties and can significantly reduce electricity costs.

**Key aspects of solar PV:**
- **Technology:** Crystalline silicon dominates the market
- **Components:** Panels, inverters, mounting, monitoring
- **Economics:** Costs have dropped 90% since 2010
- **Environmental:** Zero emissions during operation

Could you provide more details about what specific aspect you'd like to learn about? I can help with system sizing, installation, standards, economics, or technical specifications."""

    async def generate_response(
        self,
        query: str,
        expertise_level: ExpertiseLevel = ExpertiseLevel.INTERMEDIATE,
        conversation_id: Optional[str] = None,
        include_citations: bool = True
    ) -> tuple[str, List[Citation], str, float, List[str]]:
        """Generate a response to a user query."""

        # Generate or use conversation ID
        conv_id = conversation_id or str(uuid.uuid4())

        # Generate mock response (replace with actual LLM call in production)
        response, citations, follow_ups = self._generate_mock_response(
            query, expertise_level, include_citations
        )

        # Mock confidence score
        confidence = 0.85

        return response, citations, conv_id, confidence, follow_ups

    async def stream_response(
        self,
        query: str,
        expertise_level: ExpertiseLevel = ExpertiseLevel.INTERMEDIATE,
        conversation_id: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens for real-time chat."""

        # Get the full response first
        response, _, _, _, _ = await self.generate_response(
            query, expertise_level, conversation_id, include_citations=False
        )

        # Simulate streaming by yielding word by word
        words = response.split()
        for i, word in enumerate(words):
            if i > 0:
                yield " "
            yield word


# Singleton instance
llm_service = LLMService()
