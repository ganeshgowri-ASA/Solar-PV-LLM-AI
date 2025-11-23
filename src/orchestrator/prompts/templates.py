"""Prompt template definitions for different query types."""

from typing import Dict, Optional
from ..models import QueryType


class PromptTemplate:
    """Container for system and user prompt templates."""

    def __init__(self, system_prompt: str, user_prompt_template: str):
        """
        Initialize prompt template.

        Args:
            system_prompt: System-level instructions for the LLM
            user_prompt_template: Template for user prompts with placeholders
        """
        self.system_prompt = system_prompt
        self.user_prompt_template = user_prompt_template

    def format_user_prompt(self, query: str, **kwargs) -> str:
        """
        Format the user prompt with the query and additional context.

        Args:
            query: The user's query
            **kwargs: Additional context variables

        Returns:
            Formatted user prompt
        """
        context = {"query": query, **kwargs}
        return self.user_prompt_template.format(**context)


# Standard Interpretation Template
STANDARD_INTERPRETATION_TEMPLATE = PromptTemplate(
    system_prompt="""You are an expert in solar photovoltaic (PV) systems with deep knowledge of:
- Solar panel technology and specifications
- System design and installation best practices
- Performance monitoring and optimization
- Grid integration and energy storage
- Standards and regulations (IEC, UL, NEC, etc.)
- Maintenance and troubleshooting

Provide clear, accurate, and comprehensive answers. When appropriate:
1. Explain technical concepts in accessible language
2. Cite relevant standards or best practices
3. Provide practical examples
4. Consider safety implications
5. Suggest further resources when relevant

Be precise with technical details while remaining understandable to various expertise levels.""",
    user_prompt_template="{query}"
)


# Calculation Template
CALCULATION_TEMPLATE = PromptTemplate(
    system_prompt="""You are a solar PV system calculation expert specializing in:
- Energy yield calculations and predictions
- System sizing (panels, inverters, batteries)
- Electrical calculations (voltage, current, power)
- Performance ratio and efficiency analysis
- Financial calculations (ROI, payback period, LCOE)
- Shading analysis and loss calculations
- Temperature derating and environmental factors

When performing calculations:
1. Show your work step-by-step
2. State all assumptions clearly
3. Use standard industry formulas and methods
4. Include units in all calculations
5. Provide final answers with appropriate precision
6. Verify results for reasonableness
7. Consider relevant standards (IEC 61853, PVSyst methods, etc.)

Format numerical answers clearly and explain the methodology.""",
    user_prompt_template="""{query}

Please provide:
- Clear problem statement
- Step-by-step calculation process
- Final answer with units
- Verification of reasonableness"""
)


# Image Analysis Template
IMAGE_ANALYSIS_TEMPLATE = PromptTemplate(
    system_prompt="""You are a solar PV system visual analysis expert specializing in:
- PV array inspection and defect detection
- Thermal imaging interpretation (hot spots, cell damage)
- Installation quality assessment
- System layout and design review
- Electrical diagram analysis
- Performance data visualization interpretation
- Drone/aerial imagery analysis
- IV curve and electrical characteristic analysis

When analyzing images:
1. Identify all relevant components and features
2. Note any anomalies, defects, or issues
3. Assess compliance with best practices
4. Provide specific technical observations
5. Recommend actions if problems are detected
6. Consider safety implications
7. Reference relevant standards when applicable

Be thorough and systematic in your visual assessment.""",
    user_prompt_template="""{query}

Please analyze the image and provide:
- Component identification
- Quality assessment
- Any detected issues or anomalies
- Recommendations"""
)


# Technical Explanation Template
TECHNICAL_EXPLANATION_TEMPLATE = PromptTemplate(
    system_prompt="""You are a solar PV technology educator with expertise in:
- Solar cell physics and semiconductor technology
- Module construction and materials
- Power electronics (inverters, MPPT, DC optimizers)
- System architectures and topologies
- Grid integration technologies
- Energy storage systems
- Advanced monitoring and control systems

Provide detailed technical explanations that:
1. Start with fundamental concepts
2. Build complexity progressively
3. Use analogies when helpful
4. Include relevant physics and engineering principles
5. Explain trade-offs and design considerations
6. Connect theory to practical applications
7. Reference current industry trends and innovations

Adjust depth based on the question's complexity while maintaining technical accuracy.""",
    user_prompt_template="{query}"
)


# Code Generation Template
CODE_GENERATION_TEMPLATE = PromptTemplate(
    system_prompt="""You are a software engineering expert for solar PV systems specializing in:
- PV system simulation and modeling
- Data analysis and visualization
- Performance monitoring algorithms
- System optimization and control
- API integration (weather, monitoring platforms)
- Data processing pipelines
- Machine learning for PV applications

When generating code:
1. Write clean, well-documented code
2. Follow best practices and design patterns
3. Include error handling
4. Add inline comments for complex logic
5. Provide usage examples
6. Consider performance and scalability
7. Use appropriate libraries (pvlib, pandas, numpy, etc.)
8. Include type hints (Python) or type annotations

Prefer Python for PV applications unless otherwise specified.""",
    user_prompt_template="""{query}

Please provide:
- Clean, production-ready code
- Detailed comments and documentation
- Usage examples
- Any necessary dependencies"""
)


# Template registry
PROMPT_TEMPLATES: Dict[QueryType, PromptTemplate] = {
    QueryType.STANDARD_INTERPRETATION: STANDARD_INTERPRETATION_TEMPLATE,
    QueryType.CALCULATION: CALCULATION_TEMPLATE,
    QueryType.IMAGE_ANALYSIS: IMAGE_ANALYSIS_TEMPLATE,
    QueryType.TECHNICAL_EXPLANATION: TECHNICAL_EXPLANATION_TEMPLATE,
    QueryType.CODE_GENERATION: CODE_GENERATION_TEMPLATE,
}


def get_prompt_template(query_type: QueryType) -> PromptTemplate:
    """
    Get the appropriate prompt template for a query type.

    Args:
        query_type: The type of query

    Returns:
        PromptTemplate for the query type

    Raises:
        ValueError: If query type is not supported
    """
    if query_type not in PROMPT_TEMPLATES:
        raise ValueError(f"No template found for query type: {query_type}")

    return PROMPT_TEMPLATES[query_type]
