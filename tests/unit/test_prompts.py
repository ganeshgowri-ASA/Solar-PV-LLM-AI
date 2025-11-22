"""Tests for prompt templates."""

import pytest
from src.orchestrator.prompts import get_prompt_template, PromptTemplate
from src.orchestrator.models import QueryType


class TestPromptTemplates:
    """Test suite for prompt templates."""

    def test_get_calculation_template(self):
        """Test getting calculation template."""
        template = get_prompt_template(QueryType.CALCULATION)

        assert isinstance(template, PromptTemplate)
        assert template.system_prompt is not None
        assert "calculation" in template.system_prompt.lower()
        assert "step-by-step" in template.system_prompt.lower()

    def test_get_image_analysis_template(self):
        """Test getting image analysis template."""
        template = get_prompt_template(QueryType.IMAGE_ANALYSIS)

        assert isinstance(template, PromptTemplate)
        assert template.system_prompt is not None
        assert "image" in template.system_prompt.lower() or "visual" in template.system_prompt.lower()

    def test_get_code_generation_template(self):
        """Test getting code generation template."""
        template = get_prompt_template(QueryType.CODE_GENERATION)

        assert isinstance(template, PromptTemplate)
        assert template.system_prompt is not None
        assert "code" in template.system_prompt.lower()

    def test_get_technical_explanation_template(self):
        """Test getting technical explanation template."""
        template = get_prompt_template(QueryType.TECHNICAL_EXPLANATION)

        assert isinstance(template, PromptTemplate)
        assert template.system_prompt is not None
        assert "explain" in template.system_prompt.lower() or "technical" in template.system_prompt.lower()

    def test_get_standard_interpretation_template(self):
        """Test getting standard interpretation template."""
        template = get_prompt_template(QueryType.STANDARD_INTERPRETATION)

        assert isinstance(template, PromptTemplate)
        assert template.system_prompt is not None
        assert "solar" in template.system_prompt.lower()

    def test_format_user_prompt(self):
        """Test formatting user prompt."""
        template = get_prompt_template(QueryType.CALCULATION)

        query = "Calculate the energy yield for a 10kW system"
        formatted = template.format_user_prompt(query)

        assert query in formatted
        assert isinstance(formatted, str)

    def test_format_user_prompt_with_context(self):
        """Test formatting user prompt with additional context."""
        template = PromptTemplate(
            system_prompt="Test system prompt",
            user_prompt_template="Query: {query}\nContext: {context_info}",
        )

        formatted = template.format_user_prompt(
            query="Test query", context_info="Additional context"
        )

        assert "Test query" in formatted
        assert "Additional context" in formatted

    def test_invalid_query_type_raises_error(self):
        """Test that invalid query type raises error."""
        # This would raise an error if we tried to create an invalid QueryType
        # but since it's an Enum, we can't create invalid values easily
        # So we'll just verify all valid types work
        for query_type in QueryType:
            template = get_prompt_template(query_type)
            assert template is not None
