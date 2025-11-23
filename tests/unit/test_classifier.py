"""Tests for the semantic classifier."""

import pytest
from src.orchestrator.classifier import SemanticClassifier
from src.orchestrator.models import QueryType


class TestSemanticClassifier:
    """Test suite for SemanticClassifier."""

    @pytest.fixture
    def classifier(self):
        """Create classifier instance."""
        return SemanticClassifier()

    def test_classify_calculation_query(self, classifier):
        """Test classification of calculation queries."""
        queries = [
            "Calculate the energy yield for a 10kW system",
            "How many solar panels do I need for 5000 kWh per year?",
            "Determine the ROI for this solar installation",
            "What is the system size needed for 20kWh daily consumption?",
        ]

        for query in queries:
            result = classifier.classify(query)
            assert result.query_type == QueryType.CALCULATION
            assert result.confidence > 0.3
            assert result.reasoning is not None

    def test_classify_image_analysis_query(self, classifier):
        """Test classification of image analysis queries."""
        queries = [
            "Analyze this thermal image of the solar array",
            "What defects do you see in this photo?",
            "Inspect the hot spots in this drone image",
        ]

        for query in queries:
            result = classifier.classify(query, image_data=True)
            assert result.query_type == QueryType.IMAGE_ANALYSIS
            assert result.confidence >= 0.95  # High confidence with image data

    def test_classify_code_generation_query(self, classifier):
        """Test classification of code generation queries."""
        queries = [
            "Write a Python script to calculate shading losses",
            "Generate code for PV system simulation using pvlib",
            "Create a function to analyze solar panel performance",
        ]

        for query in queries:
            result = classifier.classify(query)
            assert result.query_type == QueryType.CODE_GENERATION
            assert result.confidence > 0.3

    def test_classify_technical_explanation_query(self, classifier):
        """Test classification of technical explanation queries."""
        queries = [
            "How does MPPT tracking work?",
            "Explain the principle of the photovoltaic effect",
            "What is the difference between string and micro inverters?",
            "Why do solar panels lose efficiency over time?",
        ]

        for query in queries:
            result = classifier.classify(query)
            assert result.query_type == QueryType.TECHNICAL_EXPLANATION
            assert result.confidence > 0.3

    def test_classify_standard_interpretation_query(self, classifier):
        """Test classification of standard queries."""
        query = "Tell me about solar panels"
        result = classifier.classify(query)

        # Should default to standard interpretation for ambiguous queries
        assert result.query_type in [
            QueryType.STANDARD_INTERPRETATION,
            QueryType.TECHNICAL_EXPLANATION,
        ]
        assert 0 <= result.confidence <= 1.0

    def test_classify_with_image_data(self, classifier):
        """Test that image data forces IMAGE_ANALYSIS classification."""
        query = "What's wrong with this?"
        result = classifier.classify(query, image_data=True)

        assert result.query_type == QueryType.IMAGE_ANALYSIS
        assert result.confidence >= 0.95
        assert result.features["has_image"] is True

    def test_classification_confidence_bounds(self, classifier):
        """Test that confidence is always between 0 and 1."""
        queries = [
            "Calculate energy yield",
            "Analyze this image",
            "How does it work?",
            "Write code",
            "Random query",
        ]

        for query in queries:
            result = classifier.classify(query)
            assert 0 <= result.confidence <= 1.0

    def test_classification_features(self, classifier):
        """Test that classification includes feature scores."""
        query = "Calculate the system size"
        result = classifier.classify(query)

        assert result.features is not None
        assert isinstance(result.features, dict)
        assert len(result.features) > 0
