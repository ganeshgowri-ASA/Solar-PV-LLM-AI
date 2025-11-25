"""
Solar PV LLM API Client
Handles communication with the backend RAG service and Pinecone vector database.
"""

import os
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required if env vars are set directly


class ExpertiseLevel(Enum):
    """User expertise levels for tailored responses"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class CalculationType(Enum):
    """Types of solar PV calculations available"""
    SYSTEM_SIZE = "system_size"
    ENERGY_OUTPUT = "energy_output"
    ROI = "roi"
    PAYBACK_PERIOD = "payback_period"
    PANEL_COUNT = "panel_count"
    INVERTER_SIZE = "inverter_size"
    BATTERY_SIZE = "battery_size"


@dataclass
class APIResponse:
    """Standardized API response wrapper"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class SolarPVAPIClient:
    """
    API Client for Solar PV LLM system.
    Integrates with Pinecone for RAG and handles chat queries.
    """

    def __init__(self):
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_index = os.getenv("PINECONE_INDEX", "pv-expert-knowledge")
        self.pinecone_environment = os.getenv("PINECONE_ENVIRONMENT", "us-west-2")
        self._pc = None
        self._index = None

    def _get_pinecone_client(self):
        """Lazy initialization of Pinecone client"""
        if self._pc is None:
            try:
                from pinecone import Pinecone
                if self.pinecone_api_key:
                    self._pc = Pinecone(api_key=self.pinecone_api_key)
                else:
                    print("Warning: PINECONE_API_KEY not set. Using mock mode.")
                    return None
            except ImportError:
                print("Warning: pinecone package not installed. Using mock mode.")
                return None
        return self._pc

    def _get_index(self):
        """Get Pinecone index"""
        if self._index is None:
            pc = self._get_pinecone_client()
            if pc:
                try:
                    self._index = pc.Index(self.pinecone_index)
                except Exception as e:
                    print(f"Warning: Could not connect to index {self.pinecone_index}: {e}")
                    return None
        return self._index

    def chat_query(
        self,
        query: str,
        expertise_level: ExpertiseLevel = ExpertiseLevel.INTERMEDIATE,
        context: Optional[str] = None
    ) -> APIResponse:
        """
        Send a chat query to the Solar PV knowledge base.

        Args:
            query: The user's question
            expertise_level: User's expertise level for tailored responses
            context: Optional conversation context

        Returns:
            APIResponse with response text and citations
        """
        try:
            index = self._get_index()

            if index:
                # Perform RAG search using Pinecone
                results = self._search_knowledge_base(query, expertise_level)
                response_text = self._generate_response(query, results, expertise_level)
                citations = self._extract_citations(results)
            else:
                # Fallback mock response when Pinecone is not available
                response_text = self._get_mock_response(query, expertise_level)
                citations = self._get_mock_citations()

            return APIResponse(
                success=True,
                data={
                    "response": response_text,
                    "citations": citations,
                    "expertise_level": expertise_level.value
                }
            )

        except Exception as e:
            return APIResponse(
                success=False,
                error=str(e)
            )

    def _search_knowledge_base(
        self,
        query: str,
        expertise_level: ExpertiseLevel,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search Pinecone knowledge base"""
        index = self._get_index()
        if not index:
            return []

        try:
            # Apply difficulty filter based on expertise level
            filter_criteria = None
            if expertise_level == ExpertiseLevel.BEGINNER:
                filter_criteria = {"difficulty": {"$in": ["beginner", "intermediate"]}}
            elif expertise_level == ExpertiseLevel.EXPERT:
                filter_criteria = {"difficulty": {"$in": ["intermediate", "expert", "advanced"]}}

            query_dict = {
                "top_k": top_k * 2,
                "inputs": {"text": query}
            }

            if filter_criteria:
                query_dict["filter"] = filter_criteria

            results = index.search(
                namespace="solar_pv_docs",
                query=query_dict,
                rerank={
                    "model": "bge-reranker-v2-m3",
                    "top_n": top_k,
                    "rank_fields": ["content"]
                }
            )

            return results.result.hits if hasattr(results, 'result') else []

        except Exception as e:
            print(f"Search error: {e}")
            return []

    def _generate_response(
        self,
        query: str,
        results: List[Dict[str, Any]],
        expertise_level: ExpertiseLevel
    ) -> str:
        """Generate response from search results"""
        if not results:
            return self._get_mock_response(query, expertise_level)

        # Build context from results
        context_parts = []
        for i, hit in enumerate(results):
            content = hit.get('fields', {}).get('content', '')
            if content:
                context_parts.append(f"[{i+1}] {content}")

        context = "\n\n".join(context_parts)

        # For now, return formatted context (LLM integration would go here)
        return f"Based on the Solar PV knowledge base:\n\n{context}"

    def _extract_citations(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract citations from search results"""
        citations = []
        for hit in results:
            citations.append({
                "source": hit.get('_id', 'Unknown'),
                "text": hit.get('fields', {}).get('content', ''),
                "score": hit.get('_score', 0.0),
                "category": hit.get('fields', {}).get('category', 'general'),
                "section": hit.get('fields', {}).get('topic', 'General')
            })
        return citations

    def _get_mock_response(self, query: str, expertise_level: ExpertiseLevel) -> str:
        """Generate mock response when Pinecone is not available"""
        responses = {
            "solar panel": "Solar panels convert sunlight into electricity using photovoltaic cells. "
                          "These cells are made of semiconductor materials, typically silicon, that "
                          "generate an electric current when exposed to light through the photovoltaic effect.",
            "efficiency": "Modern monocrystalline solar panels typically achieve 15-22% efficiency under "
                         "standard test conditions (STC). Premium panels can reach up to 23-24% efficiency. "
                         "Factors affecting efficiency include temperature, shading, and panel orientation.",
            "installation": "Solar panel installation involves site assessment, system design, permitting, "
                           "mounting hardware installation, panel placement, electrical connections, "
                           "and final inspection. Professional installation ensures safety and optimal performance.",
            "default": "Solar photovoltaic (PV) technology converts sunlight directly into electricity. "
                      "The technology has evolved significantly, with modern systems offering high efficiency, "
                      "reliability, and decreasing costs. Key components include solar panels, inverters, "
                      "mounting systems, and monitoring equipment."
        }

        query_lower = query.lower()
        for keyword, response in responses.items():
            if keyword in query_lower:
                return response

        return responses["default"]

    def _get_mock_citations(self) -> List[Dict[str, Any]]:
        """Generate mock citations for demo purposes"""
        return [
            {
                "source": "IEC 61215",
                "text": "Terrestrial photovoltaic (PV) modules - Design qualification and type approval",
                "score": 0.92,
                "page": 1,
                "section": "Standards"
            },
            {
                "source": "NREL Technical Report",
                "text": "Best Practices for Solar PV System Installation",
                "score": 0.88,
                "page": 15,
                "section": "Installation Guidelines"
            }
        ]

    def search_standards(
        self,
        query: str,
        standard_types: Optional[List[str]] = None
    ) -> APIResponse:
        """
        Search Solar PV standards library.

        Args:
            query: Search query
            standard_types: Filter by standard types (IEC, IEEE, UL, etc.)

        Returns:
            APIResponse with matching standards
        """
        try:
            # Mock standards data
            standards = [
                {
                    "id": "IEC 61215",
                    "title": "Crystalline Silicon Terrestrial PV Modules - Design Qualification",
                    "type": "IEC",
                    "description": "International standard for crystalline silicon PV module design qualification and type approval.",
                    "year": 2021,
                    "relevance": 0.95
                },
                {
                    "id": "IEC 61730",
                    "title": "PV Module Safety Qualification",
                    "type": "IEC",
                    "description": "Requirements for photovoltaic module safety qualification.",
                    "year": 2016,
                    "relevance": 0.90
                },
                {
                    "id": "IEEE 1547",
                    "title": "Standard for Interconnection and Interoperability",
                    "type": "IEEE",
                    "description": "Interconnection of distributed energy resources with electric power systems.",
                    "year": 2018,
                    "relevance": 0.85
                },
                {
                    "id": "UL 1703",
                    "title": "Flat-Plate Photovoltaic Modules and Panels",
                    "type": "UL",
                    "description": "Safety standard for flat-plate PV modules.",
                    "year": 2021,
                    "relevance": 0.82
                }
            ]

            # Filter by type if specified
            if standard_types:
                standards = [s for s in standards if s["type"] in standard_types]

            # Simple relevance filtering based on query
            query_lower = query.lower()
            filtered = [s for s in standards if
                       query_lower in s["title"].lower() or
                       query_lower in s["description"].lower() or
                       query_lower in s["id"].lower()]

            if not filtered:
                filtered = standards  # Return all if no matches

            return APIResponse(
                success=True,
                data={"standards": filtered, "total": len(filtered)}
            )

        except Exception as e:
            return APIResponse(success=False, error=str(e))

    def calculate_system_size(
        self,
        annual_consumption_kwh: float,
        location_factor: float = 1.0,
        panel_wattage: int = 400,
        system_losses: float = 0.14
    ) -> APIResponse:
        """
        Calculate recommended solar system size.

        Args:
            annual_consumption_kwh: Annual electricity consumption in kWh
            location_factor: Location-based solar irradiance factor (0.7-1.3)
            panel_wattage: Individual panel wattage
            system_losses: System efficiency losses (default 14%)

        Returns:
            APIResponse with system sizing recommendations
        """
        try:
            # Average peak sun hours (adjust by location)
            peak_sun_hours = 4.5 * location_factor

            # Daily production per kW of panels
            daily_production_per_kw = peak_sun_hours * (1 - system_losses)

            # Annual production per kW
            annual_production_per_kw = daily_production_per_kw * 365

            # Required system size
            required_kw = annual_consumption_kwh / annual_production_per_kw

            # Number of panels
            num_panels = int((required_kw * 1000) / panel_wattage) + 1

            # Actual system size
            actual_kw = (num_panels * panel_wattage) / 1000

            # Estimated annual production
            estimated_production = actual_kw * annual_production_per_kw

            return APIResponse(
                success=True,
                data={
                    "recommended_size_kw": round(required_kw, 2),
                    "actual_size_kw": round(actual_kw, 2),
                    "num_panels": num_panels,
                    "panel_wattage": panel_wattage,
                    "estimated_annual_production_kwh": round(estimated_production, 0),
                    "coverage_percentage": round((estimated_production / annual_consumption_kwh) * 100, 1),
                    "assumptions": {
                        "peak_sun_hours": peak_sun_hours,
                        "system_losses": system_losses,
                        "location_factor": location_factor
                    }
                }
            )

        except Exception as e:
            return APIResponse(success=False, error=str(e))


# Singleton client instance
_client_instance = None


def get_client() -> SolarPVAPIClient:
    """Get or create the API client singleton"""
    global _client_instance
    if _client_instance is None:
        _client_instance = SolarPVAPIClient()
    return _client_instance
