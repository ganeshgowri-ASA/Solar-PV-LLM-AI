"""RAG Service for Solar PV Standards Search."""

from typing import List, Optional
from ..models.schemas import StandardDocument


class RAGService:
    """Service for Retrieval-Augmented Generation with solar PV standards."""

    def __init__(self):
        # Mock database of solar PV standards
        self.standards_db: List[StandardDocument] = self._init_standards_db()

    def _init_standards_db(self) -> List[StandardDocument]:
        """Initialize mock standards database."""
        return [
            StandardDocument(
                id="iec-61724-1",
                title="Photovoltaic system performance - Part 1: Monitoring",
                standard_code="IEC 61724-1:2021",
                category="Performance",
                summary="Defines methods for monitoring and analyzing the performance of photovoltaic systems, including energy yield assessment and performance ratio calculations.",
                relevance_score=0.0,
                sections=["Energy measurement", "Performance metrics", "Data requirements"]
            ),
            StandardDocument(
                id="iec-61730-1",
                title="Photovoltaic module safety qualification - Part 1: Requirements for construction",
                standard_code="IEC 61730-1:2016",
                category="Safety",
                summary="Specifies the construction requirements for PV module safety to provide safe electrical and mechanical operation during their expected lifetime.",
                relevance_score=0.0,
                sections=["General requirements", "Materials", "Electrical design"]
            ),
            StandardDocument(
                id="iec-62446-1",
                title="Photovoltaic systems - Requirements for testing, documentation and maintenance - Part 1: Grid connected systems",
                standard_code="IEC 62446-1:2016",
                category="Installation",
                summary="Defines the information and documentation required for grid-connected PV systems, along with commissioning tests and inspection criteria.",
                relevance_score=0.0,
                sections=["Documentation", "Commissioning tests", "Periodic inspection"]
            ),
            StandardDocument(
                id="nec-690",
                title="Solar Photovoltaic (PV) Systems",
                standard_code="NEC Article 690",
                category="Electrical",
                summary="Covers the installation of solar photovoltaic systems including electrical installation requirements, wiring methods, grounding, and disconnecting means.",
                relevance_score=0.0,
                sections=["Circuit requirements", "Disconnecting means", "Wiring methods", "Grounding"]
            ),
            StandardDocument(
                id="ieee-1547",
                title="Standard for Interconnection and Interoperability of Distributed Energy Resources",
                standard_code="IEEE 1547-2018",
                category="Grid Integration",
                summary="Establishes criteria and requirements for interconnection of distributed energy resources with electric power systems and associated interfaces.",
                relevance_score=0.0,
                sections=["Performance requirements", "Reactive power", "Voltage regulation"]
            ),
            StandardDocument(
                id="iec-61853-1",
                title="Photovoltaic module performance testing - Part 1: Irradiance and temperature performance measurements",
                standard_code="IEC 61853-1:2011",
                category="Performance",
                summary="Describes requirements for measuring PV module performance over a range of irradiances and temperatures to determine the annual energy yield.",
                relevance_score=0.0,
                sections=["Test conditions", "Performance matrices", "Measurement procedures"]
            ),
            StandardDocument(
                id="ul-1703",
                title="Flat-Plate Photovoltaic Modules and Panels",
                standard_code="UL 1703",
                category="Safety",
                summary="Safety standard for flat-plate photovoltaic modules and panels intended for installation on or in buildings or to be freestanding.",
                relevance_score=0.0,
                sections=["Construction", "Performance", "Marking"]
            ),
            StandardDocument(
                id="iec-62109-1",
                title="Safety of power converters for photovoltaic power systems - Part 1: General requirements",
                standard_code="IEC 62109-1:2010",
                category="Inverters",
                summary="Defines safety requirements for power converters used in PV systems, including inverters and charge controllers.",
                relevance_score=0.0,
                sections=["Protection against electric shock", "Mechanical hazards", "Temperature limits"]
            ),
            StandardDocument(
                id="iec-62548",
                title="Photovoltaic arrays - Design requirements",
                standard_code="IEC 62548:2016",
                category="Design",
                summary="Sets out design requirements for PV arrays including DC array design, electrical protection, and array structures.",
                relevance_score=0.0,
                sections=["Array design", "Protection devices", "Documentation"]
            ),
            StandardDocument(
                id="astm-e2848",
                title="Standard Test Method for Reporting Photovoltaic Non-Concentrator System Performance",
                standard_code="ASTM E2848",
                category="Performance",
                summary="Describes a methodology for reporting the capacity of non-concentrator photovoltaic systems under controlled conditions.",
                relevance_score=0.0,
                sections=["Test method", "Reporting", "Performance metrics"]
            ),
        ]

    def _calculate_relevance(self, doc: StandardDocument, query: str) -> float:
        """Calculate relevance score for a document based on query."""
        query_lower = query.lower()
        score = 0.0

        # Check title match
        if any(word in doc.title.lower() for word in query_lower.split()):
            score += 0.4

        # Check standard code match
        if any(word in doc.standard_code.lower() for word in query_lower.split()):
            score += 0.3

        # Check summary match
        summary_words = doc.summary.lower()
        matching_words = sum(1 for word in query_lower.split() if word in summary_words)
        score += min(0.3, matching_words * 0.1)

        # Check category match
        if doc.category.lower() in query_lower:
            score += 0.2

        # Keyword boosts
        keywords = {
            "safety": ["safety", "hazard", "protection", "ul", "certification"],
            "performance": ["performance", "efficiency", "output", "yield", "monitoring"],
            "installation": ["install", "mount", "wiring", "commissioning"],
            "grid": ["grid", "interconnection", "utility", "ieee"],
            "inverter": ["inverter", "converter", "power electronics"],
        }

        for category, words in keywords.items():
            if any(w in query_lower for w in words):
                if category.lower() in doc.category.lower():
                    score += 0.15

        return min(1.0, score)

    async def search_standards(
        self,
        query: str,
        categories: Optional[List[str]] = None,
        max_results: int = 10,
        include_summaries: bool = True
    ) -> tuple[List[StandardDocument], int, List[str]]:
        """Search solar PV standards database."""

        results = []

        for doc in self.standards_db:
            # Filter by categories if specified
            if categories and doc.category not in categories:
                continue

            # Calculate relevance
            relevance = self._calculate_relevance(doc, query)

            if relevance > 0.1:  # Minimum threshold
                result = StandardDocument(
                    id=doc.id,
                    title=doc.title,
                    standard_code=doc.standard_code,
                    category=doc.category,
                    summary=doc.summary if include_summaries else "",
                    relevance_score=relevance,
                    sections=doc.sections
                )
                results.append(result)

        # Sort by relevance
        results.sort(key=lambda x: x.relevance_score, reverse=True)

        # Get unique categories
        categories_found = list(set(doc.category for doc in results))

        # Limit results
        limited_results = results[:max_results]

        return limited_results, len(results), categories_found

    def get_categories(self) -> List[str]:
        """Get all available categories."""
        return list(set(doc.category for doc in self.standards_db))


# Singleton instance
rag_service = RAGService()
