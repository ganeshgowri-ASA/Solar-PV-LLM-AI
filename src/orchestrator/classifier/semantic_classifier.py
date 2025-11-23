"""Semantic query classifier using pattern matching and keyword analysis."""

import re
from typing import Dict, List, Tuple
from loguru import logger

from ..models import QueryType, ClassificationResult


class SemanticClassifier:
    """
    Classifies queries into different types using semantic analysis.

    Uses a combination of:
    - Keyword matching
    - Pattern recognition
    - Linguistic features
    - Domain-specific indicators
    """

    def __init__(self):
        """Initialize the classifier with patterns and keywords."""
        self.patterns = self._initialize_patterns()
        self.keywords = self._initialize_keywords()

    def _initialize_patterns(self) -> Dict[QueryType, List[re.Pattern]]:
        """Initialize regex patterns for each query type."""
        return {
            QueryType.CALCULATION: [
                re.compile(r'\bcalculat(e|ion|ing)\b', re.IGNORECASE),
                re.compile(r'\bcompute\b', re.IGNORECASE),
                re.compile(r'\bhow (much|many)\b', re.IGNORECASE),
                re.compile(r'\bsize\s+(the\s+)?system\b', re.IGNORECASE),
                re.compile(r'\benergy\s+yield\b', re.IGNORECASE),
                re.compile(r'\b(determine|find)\s+(the\s+)?(size|capacity|power|voltage|current)\b', re.IGNORECASE),
                re.compile(r'\bROI\b|\breturn on investment\b', re.IGNORECASE),
                re.compile(r'\bpayback\s+period\b', re.IGNORECASE),
                re.compile(r'\bLCOE\b|\blevelized cost\b', re.IGNORECASE),
                re.compile(r'\d+\s*(kW|MW|W|V|A|Wh|kWh|MWh)', re.IGNORECASE),
                re.compile(r'\bperformance\s+ratio\b', re.IGNORECASE),
            ],
            QueryType.IMAGE_ANALYSIS: [
                re.compile(r'\bimage\b|\bphoto\b|\bpicture\b', re.IGNORECASE),
                re.compile(r'\bthermal\s+image\b|\bthermal\s+imaging\b', re.IGNORECASE),
                re.compile(r'\binspect(ion)?\b.*\bimage\b', re.IGNORECASE),
                re.compile(r'\banalyze\s+(this\s+)?(image|photo|picture)\b', re.IGNORECASE),
                re.compile(r'\bhot\s*spot\b', re.IGNORECASE),
                re.compile(r'\bvisual\s+inspection\b', re.IGNORECASE),
                re.compile(r'\bdrone\s+(image|imagery)\b', re.IGNORECASE),
                re.compile(r'\bIV\s+curve\b', re.IGNORECASE),
            ],
            QueryType.CODE_GENERATION: [
                re.compile(r'\bwrite\s+(a\s+)?(script|code|program|function)\b', re.IGNORECASE),
                re.compile(r'\bgenerate\s+code\b', re.IGNORECASE),
                re.compile(r'\bimplement\s+(a|an)\b', re.IGNORECASE),
                re.compile(r'\bcreate\s+(a\s+)?(function|class|module)\b', re.IGNORECASE),
                re.compile(r'\b(python|javascript|java)\s+code\b', re.IGNORECASE),
                re.compile(r'\bpvlib\b|\bpandas\b|\bnumpy\b', re.IGNORECASE),
                re.compile(r'\bAPI\s+(call|integration)\b', re.IGNORECASE),
                re.compile(r'\bsimulat(e|ion)\s+code\b', re.IGNORECASE),
            ],
            QueryType.TECHNICAL_EXPLANATION: [
                re.compile(r'\bhow\s+(does|do)\b.*\bwork\b', re.IGNORECASE),
                re.compile(r'\bwhat\s+is\s+(the\s+)?(difference|principle)\b', re.IGNORECASE),
                re.compile(r'\bexplain\b', re.IGNORECASE),
                re.compile(r'\bwhy\s+(does|do|is|are)\b', re.IGNORECASE),
                re.compile(r'\bMPPT\b|\bmaximum\s+power\s+point\b', re.IGNORECASE),
                re.compile(r'\binverter\s+(technology|topology|working)\b', re.IGNORECASE),
                re.compile(r'\bphysics\s+of\b|\bprinciple\s+of\b', re.IGNORECASE),
                re.compile(r'\bcompare\b.*\b(vs|versus)\b', re.IGNORECASE),
            ],
        }

    def _initialize_keywords(self) -> Dict[QueryType, List[str]]:
        """Initialize keyword sets for each query type."""
        return {
            QueryType.CALCULATION: [
                'calculate', 'compute', 'size', 'sizing', 'determine',
                'kwh', 'mwh', 'kw', 'mw', 'watts', 'voltage', 'current',
                'efficiency', 'yield', 'capacity', 'output', 'production',
                'roi', 'payback', 'lcoe', 'cost', 'savings', 'performance ratio'
            ],
            QueryType.IMAGE_ANALYSIS: [
                'image', 'photo', 'picture', 'thermal', 'inspect', 'inspection',
                'visual', 'drone', 'aerial', 'hotspot', 'hot spot', 'defect',
                'iv curve', 'diagram', 'layout', 'soiling'
            ],
            QueryType.CODE_GENERATION: [
                'code', 'script', 'program', 'function', 'implement', 'write',
                'python', 'javascript', 'api', 'pvlib', 'pandas', 'algorithm',
                'simulate', 'model', 'automate'
            ],
            QueryType.TECHNICAL_EXPLANATION: [
                'explain', 'how', 'why', 'what', 'principle', 'work', 'works',
                'difference', 'compare', 'mppt', 'inverter', 'physics',
                'technology', 'architecture', 'topology'
            ],
        }

    def classify(self, query: str, image_data: bool = False) -> ClassificationResult:
        """
        Classify a query into a specific type.

        Args:
            query: The user's query text
            image_data: Whether image data is provided

        Returns:
            ClassificationResult with query type and confidence
        """
        logger.debug(f"Classifying query: {query[:100]}...")

        # If image data is provided, it's likely image analysis
        if image_data:
            return ClassificationResult(
                query_type=QueryType.IMAGE_ANALYSIS,
                confidence=0.95,
                reasoning="Image data provided with query",
                features={'has_image': True}
            )

        # Calculate scores for each query type
        scores = self._calculate_scores(query)

        # Get the highest scoring type
        best_type, confidence = self._get_best_match(scores)

        # Default to standard interpretation if confidence is too low
        if confidence < 0.3:
            best_type = QueryType.STANDARD_INTERPRETATION
            confidence = 0.5

        result = ClassificationResult(
            query_type=best_type,
            confidence=confidence,
            reasoning=self._get_reasoning(query, best_type, scores),
            features=scores
        )

        logger.info(
            f"Query classified as {best_type.value} "
            f"(confidence: {confidence:.2f})"
        )

        return result

    def _calculate_scores(self, query: str) -> Dict[str, float]:
        """Calculate classification scores for all query types."""
        scores = {}
        query_lower = query.lower()

        for query_type in [
            QueryType.CALCULATION,
            QueryType.IMAGE_ANALYSIS,
            QueryType.CODE_GENERATION,
            QueryType.TECHNICAL_EXPLANATION
        ]:
            # Pattern matching score
            pattern_score = self._pattern_score(query, query_type)

            # Keyword score
            keyword_score = self._keyword_score(query_lower, query_type)

            # Combined score (weighted average)
            combined_score = (pattern_score * 0.6) + (keyword_score * 0.4)

            scores[query_type.value] = combined_score

        return scores

    def _pattern_score(self, query: str, query_type: QueryType) -> float:
        """Calculate pattern matching score."""
        if query_type not in self.patterns:
            return 0.0

        matches = sum(
            1 for pattern in self.patterns[query_type]
            if pattern.search(query)
        )

        # Normalize by number of patterns
        return min(matches / max(len(self.patterns[query_type]), 1), 1.0)

    def _keyword_score(self, query_lower: str, query_type: QueryType) -> float:
        """Calculate keyword matching score."""
        if query_type not in self.keywords:
            return 0.0

        matches = sum(
            1 for keyword in self.keywords[query_type]
            if keyword in query_lower
        )

        # Normalize by number of keywords
        return min(matches / max(len(self.keywords[query_type]), 1), 1.0) * 2

    def _get_best_match(
        self,
        scores: Dict[str, float]
    ) -> Tuple[QueryType, float]:
        """Get the query type with the highest score."""
        if not scores:
            return QueryType.STANDARD_INTERPRETATION, 0.5

        best_type_str = max(scores, key=scores.get)
        confidence = scores[best_type_str]

        # Convert string back to QueryType
        best_type = QueryType(best_type_str)

        return best_type, confidence

    def _get_reasoning(
        self,
        query: str,
        classified_type: QueryType,
        scores: Dict[str, float]
    ) -> str:
        """Generate reasoning for the classification."""
        top_scores = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:2]

        reasoning_parts = [
            f"Classified as {classified_type.value} with score {scores[classified_type.value]:.2f}."
        ]

        if len(top_scores) > 1 and top_scores[1][1] > 0.2:
            reasoning_parts.append(
                f"Alternative: {top_scores[1][0]} (score: {top_scores[1][1]:.2f})."
            )

        return " ".join(reasoning_parts)
