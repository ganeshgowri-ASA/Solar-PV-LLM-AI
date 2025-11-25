"""
Solar PV LLM API Client
Handles communication with the backend RAG service and Pinecone vector database.
"""

import os
import uuid
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Iterator, Union

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

    def is_healthy(self) -> bool:
        """
        Check if the backend/API is healthy and responsive.

        Returns:
            True if healthy, False otherwise
        """
        try:
            # Try to initialize Pinecone client
            pc = self._get_pinecone_client()
            if pc:
                # If Pinecone client initializes, we're healthy
                return True
            # Even without Pinecone, we can run in mock mode
            return True
        except Exception:
            return False

    def chat_query(
        self,
        query: str,
        expertise_level: ExpertiseLevel = ExpertiseLevel.INTERMEDIATE,
        context: Optional[str] = None,
        conversation_id: Optional[str] = None,
        include_citations: bool = True
    ) -> APIResponse:
        """
        Send a chat query to the Solar PV knowledge base.

        Args:
            query: The user's question
            expertise_level: User's expertise level for tailored responses
            context: Optional conversation context
            conversation_id: Optional conversation ID for context tracking
            include_citations: Whether to include citations in response

        Returns:
            APIResponse with response text and citations
        """
        try:
            index = self._get_index()

            if index:
                # Perform RAG search using Pinecone
                results = self._search_knowledge_base(query, expertise_level)
                response_text = self._generate_response(query, results, expertise_level)
                citations = self._extract_citations(results) if include_citations else []
            else:
                # Fallback mock response when Pinecone is not available
                response_text = self._get_mock_response(query, expertise_level)
                citations = self._get_mock_citations() if include_citations else []

            # Generate conversation ID if not provided
            if not conversation_id:
                conversation_id = str(uuid.uuid4())

            return APIResponse(
                success=True,
                data={
                    "response": response_text,
                    "citations": citations,
                    "expertise_level": expertise_level.value,
                    "conversation_id": conversation_id,
                    "follow_up_questions": self._generate_follow_up_questions(query)
                }
            )

        except Exception as e:
            return APIResponse(
                success=False,
                error=str(e)
            )

    def chat_stream(
        self,
        query: str,
        expertise_level: ExpertiseLevel = ExpertiseLevel.INTERMEDIATE,
        conversation_id: Optional[str] = None
    ) -> Iterator[str]:
        """
        Stream a chat response token by token.

        Args:
            query: The user's question
            expertise_level: User's expertise level for tailored responses
            conversation_id: Optional conversation ID for context tracking

        Yields:
            Response tokens one at a time
        """
        # Get the full response
        response = self.chat_query(
            query=query,
            expertise_level=expertise_level,
            conversation_id=conversation_id,
            include_citations=False
        )

        if response.success and response.data:
            full_text = response.data.get("response", "")
            # Simulate streaming by yielding words
            words = full_text.split()
            for word in words:
                yield word + " "
        else:
            yield f"Error: {response.error or 'Unknown error'}"

    def _generate_follow_up_questions(self, query: str) -> List[str]:
        """Generate suggested follow-up questions based on the query."""
        query_lower = query.lower()

        if "efficiency" in query_lower:
            return [
                "How can I improve panel efficiency?",
                "What affects solar panel degradation?"
            ]
        elif "install" in query_lower:
            return [
                "What permits are needed?",
                "How long does installation take?"
            ]
        elif "cost" in query_lower or "price" in query_lower:
            return [
                "What incentives are available?",
                "How do I calculate ROI?"
            ]
        elif "battery" in query_lower or "storage" in query_lower:
            return [
                "What battery types are best?",
                "How do I size a battery system?"
            ]
        else:
            return [
                "What system size do I need?",
                "How much can I save?"
            ]

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

    def get_categories(self) -> APIResponse:
        """
        Get available document categories.

        Returns:
            APIResponse with list of categories
        """
        try:
            categories = [
                "Safety",
                "Performance",
                "Installation",
                "Electrical",
                "Design",
                "Maintenance",
                "Grid Integration",
                "Testing",
                "Certification"
            ]
            return APIResponse(success=True, data=categories)
        except Exception as e:
            return APIResponse(success=False, error=str(e))

    def search_standards(
        self,
        query: str,
        standard_types: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        max_results: int = 10,
        include_summaries: bool = True
    ) -> APIResponse:
        """
        Search Solar PV standards library.

        Args:
            query: Search query
            standard_types: Filter by standard types (IEC, IEEE, UL, etc.)
            categories: Filter by categories
            max_results: Maximum number of results to return
            include_summaries: Whether to include summaries

        Returns:
            APIResponse with matching standards
        """
        try:
            # Mock standards data
            standards = [
                {
                    "id": "std_001",
                    "standard_code": "IEC 61215",
                    "title": "Crystalline Silicon Terrestrial PV Modules - Design Qualification",
                    "type": "IEC",
                    "category": "Design",
                    "description": "International standard for crystalline silicon PV module design qualification and type approval.",
                    "summary": "This standard defines requirements for design qualification and type approval of terrestrial photovoltaic modules suitable for long-term operation in general open-air climates.",
                    "year": 2021,
                    "relevance_score": 0.95,
                    "sections": ["Design Requirements", "Test Sequences", "Qualification Criteria"]
                },
                {
                    "id": "std_002",
                    "standard_code": "IEC 61730",
                    "title": "PV Module Safety Qualification",
                    "type": "IEC",
                    "category": "Safety",
                    "description": "Requirements for photovoltaic module safety qualification.",
                    "summary": "Provides the fundamental construction requirements for photovoltaic modules in order to provide safe electrical and mechanical operation.",
                    "year": 2016,
                    "relevance_score": 0.90,
                    "sections": ["Construction Requirements", "Test Requirements", "Safety Ratings"]
                },
                {
                    "id": "std_003",
                    "standard_code": "IEEE 1547",
                    "title": "Standard for Interconnection and Interoperability",
                    "type": "IEEE",
                    "category": "Grid Integration",
                    "description": "Interconnection of distributed energy resources with electric power systems.",
                    "summary": "Establishes criteria and requirements for interconnection of distributed energy resources with electric power systems and associated interfaces.",
                    "year": 2018,
                    "relevance_score": 0.85,
                    "sections": ["Interconnection Requirements", "Testing", "Design"]
                },
                {
                    "id": "std_004",
                    "standard_code": "UL 1703",
                    "title": "Flat-Plate Photovoltaic Modules and Panels",
                    "type": "UL",
                    "category": "Safety",
                    "description": "Safety standard for flat-plate PV modules.",
                    "summary": "Covers flat-plate photovoltaic modules and panels intended for installation on or integral with buildings, or to be used as freestanding power sources.",
                    "year": 2021,
                    "relevance_score": 0.82,
                    "sections": ["General", "Construction", "Performance"]
                },
                {
                    "id": "std_005",
                    "standard_code": "IEC 62446",
                    "title": "Grid Connected PV Systems - Minimum System Documentation",
                    "type": "IEC",
                    "category": "Installation",
                    "description": "Requirements for system documentation, commissioning tests and inspection for grid connected PV systems.",
                    "summary": "Defines the minimum information and documentation required to be handed over to the customer following installation of a grid connected PV system.",
                    "year": 2020,
                    "relevance_score": 0.78,
                    "sections": ["Documentation", "Commissioning", "Inspection"]
                },
                {
                    "id": "std_006",
                    "standard_code": "IEC 61724",
                    "title": "Photovoltaic System Performance Monitoring",
                    "type": "IEC",
                    "category": "Performance",
                    "description": "Guidelines for measurement, data exchange and analysis of PV system performance.",
                    "summary": "Provides guidelines for monitoring systems for photovoltaic (PV) installations and defines parameters and methods for consistent performance reporting.",
                    "year": 2021,
                    "relevance_score": 0.75,
                    "sections": ["Monitoring Equipment", "Data Analysis", "Reporting"]
                }
            ]

            # Filter by type if specified
            if standard_types:
                standards = [s for s in standards if s["type"] in standard_types]

            # Filter by category if specified
            if categories:
                standards = [s for s in standards if s["category"] in categories]

            # Simple relevance filtering based on query
            query_lower = query.lower()
            filtered = [s for s in standards if
                       query_lower in s["title"].lower() or
                       query_lower in s["description"].lower() or
                       query_lower in s["standard_code"].lower() or
                       query_lower in s.get("category", "").lower()]

            if not filtered:
                filtered = standards  # Return all if no matches

            # Sort by relevance
            filtered.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

            # Limit results
            filtered = filtered[:max_results]

            # Remove summaries if not requested
            if not include_summaries:
                for doc in filtered:
                    doc.pop("summary", None)

            return APIResponse(
                success=True,
                data={
                    "results": filtered,
                    "total_count": len(filtered)
                }
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

    def calculate(
        self,
        calculation_type: CalculationType,
        parameters: Dict[str, Any],
        include_explanation: bool = True
    ) -> APIResponse:
        """
        Perform various solar PV calculations.

        Args:
            calculation_type: Type of calculation to perform
            parameters: Calculation parameters
            include_explanation: Whether to include explanation in response

        Returns:
            APIResponse with calculation results
        """
        try:
            result = {}
            explanation = ""
            assumptions = []
            recommendations = []

            if calculation_type == CalculationType.SYSTEM_SIZE:
                annual_kwh = parameters.get("annual_kwh", 10000)
                peak_sun_hours = parameters.get("peak_sun_hours", 5.0)
                performance_ratio = parameters.get("performance_ratio", 0.80)
                panel_wattage = parameters.get("panel_wattage", 400)

                # Calculate system size
                daily_kwh = annual_kwh / 365
                system_size_kw = daily_kwh / (peak_sun_hours * performance_ratio)
                num_panels = int((system_size_kw * 1000) / panel_wattage) + 1
                actual_size_kw = (num_panels * panel_wattage) / 1000

                result = {
                    "system_size_kw": round(system_size_kw, 2),
                    "actual_size_kw": round(actual_size_kw, 2),
                    "number_of_panels": num_panels
                }
                explanation = f"To offset {annual_kwh:,} kWh annually with {peak_sun_hours} peak sun hours and {performance_ratio:.0%} performance ratio, you need approximately {system_size_kw:.2f} kW system ({num_panels} panels at {panel_wattage}W each)."
                assumptions = [
                    f"Peak sun hours: {peak_sun_hours}",
                    f"System performance ratio: {performance_ratio:.0%}",
                    f"Panel wattage: {panel_wattage}W"
                ]
                recommendations = [
                    "Consider adding 10-20% buffer for future consumption growth",
                    "Verify peak sun hours for your specific location"
                ]

            elif calculation_type == CalculationType.ENERGY_OUTPUT:
                system_size_kw = parameters.get("system_size_kw", 6.0)
                peak_sun_hours = parameters.get("peak_sun_hours", 5.0)
                performance_ratio = parameters.get("performance_ratio", 0.80)

                daily_output = system_size_kw * peak_sun_hours * performance_ratio
                monthly_output = daily_output * 30
                annual_output = daily_output * 365

                result = {
                    "daily_kwh": round(daily_output, 2),
                    "monthly_kwh": round(monthly_output, 0),
                    "annual_kwh": round(annual_output, 0)
                }
                explanation = f"A {system_size_kw} kW system with {peak_sun_hours} peak sun hours and {performance_ratio:.0%} performance ratio will produce approximately {annual_output:,.0f} kWh per year."
                assumptions = [
                    f"System size: {system_size_kw} kW",
                    f"Peak sun hours: {peak_sun_hours}",
                    f"Performance ratio: {performance_ratio:.0%}"
                ]

            elif calculation_type == CalculationType.ROI:
                system_cost = parameters.get("system_cost", 15000)
                annual_kwh = parameters.get("annual_kwh", 8000)
                electricity_rate = parameters.get("electricity_rate", 0.12)
                annual_rate_increase = parameters.get("annual_rate_increase", 0.03)
                incentive_percent = parameters.get("incentive_percent", 30)

                net_cost = system_cost * (1 - incentive_percent / 100)
                annual_savings = annual_kwh * electricity_rate
                # 25-year calculation with rate increases
                total_savings_25yr = sum([annual_savings * ((1 + annual_rate_increase) ** year) for year in range(25)])
                roi_percent = ((total_savings_25yr - net_cost) / net_cost) * 100

                result = {
                    "net_system_cost": round(net_cost, 2),
                    "annual_savings": round(annual_savings, 2),
                    "total_savings_25yr": round(total_savings_25yr, 0),
                    "roi_percent": round(roi_percent, 1)
                }
                explanation = f"After {incentive_percent}% incentive, your net cost is ${net_cost:,.0f}. With ${annual_savings:,.0f} annual savings growing at {annual_rate_increase:.0%}/year, you'll save ${total_savings_25yr:,.0f} over 25 years for {roi_percent:.0f}% ROI."
                assumptions = [
                    f"System cost: ${system_cost:,}",
                    f"Incentive: {incentive_percent}%",
                    f"Electricity rate: ${electricity_rate}/kWh",
                    f"Annual rate increase: {annual_rate_increase:.0%}"
                ]
                recommendations = [
                    "Check for additional local incentives",
                    "Consider net metering availability in your area"
                ]

            elif calculation_type == CalculationType.PAYBACK_PERIOD:
                system_cost = parameters.get("system_cost", 15000)
                annual_kwh = parameters.get("annual_kwh", 8000)
                electricity_rate = parameters.get("electricity_rate", 0.12)
                incentive_percent = parameters.get("incentive_percent", 30)

                net_cost = system_cost * (1 - incentive_percent / 100)
                annual_savings = annual_kwh * electricity_rate
                payback_years = net_cost / annual_savings if annual_savings > 0 else float('inf')

                result = {
                    "net_cost": round(net_cost, 2),
                    "annual_savings": round(annual_savings, 2),
                    "payback_years": round(payback_years, 1)
                }
                explanation = f"With net cost of ${net_cost:,.0f} and annual savings of ${annual_savings:,.0f}, your payback period is approximately {payback_years:.1f} years."
                assumptions = [
                    f"Net system cost: ${net_cost:,}",
                    f"Annual energy savings: ${annual_savings:,}"
                ]

            elif calculation_type == CalculationType.PANEL_COUNT:
                target_kwh_annual = parameters.get("target_kwh_annual", 10000)
                panel_wattage = parameters.get("panel_wattage", 400)
                peak_sun_hours = parameters.get("peak_sun_hours", 5.0)
                efficiency_factor = parameters.get("efficiency_factor", 0.80)

                daily_kwh = target_kwh_annual / 365
                system_kw = daily_kwh / (peak_sun_hours * efficiency_factor)
                panel_count = int((system_kw * 1000) / panel_wattage) + 1

                result = {
                    "panel_count": panel_count,
                    "system_size_kw": round((panel_count * panel_wattage) / 1000, 2)
                }
                explanation = f"To produce {target_kwh_annual:,} kWh annually, you need approximately {panel_count} panels of {panel_wattage}W each."
                assumptions = [
                    f"Panel wattage: {panel_wattage}W",
                    f"Peak sun hours: {peak_sun_hours}",
                    f"Efficiency factor: {efficiency_factor:.0%}"
                ]

            elif calculation_type == CalculationType.INVERTER_SIZE:
                array_size_kw = parameters.get("array_size_kw", 6.0)
                dc_ac_ratio = parameters.get("dc_ac_ratio", 1.2)

                inverter_size_kw = array_size_kw / dc_ac_ratio

                result = {
                    "inverter_size_kw": round(inverter_size_kw, 2),
                    "dc_ac_ratio": dc_ac_ratio
                }
                explanation = f"For a {array_size_kw} kW DC array with {dc_ac_ratio} DC/AC ratio, you need approximately a {inverter_size_kw:.2f} kW inverter."
                assumptions = [
                    f"Array size: {array_size_kw} kW DC",
                    f"DC/AC ratio: {dc_ac_ratio}"
                ]
                recommendations = [
                    "Consider string inverter vs microinverter options",
                    "Ensure inverter is grid-code compliant for your location"
                ]

            elif calculation_type == CalculationType.BATTERY_SIZE:
                daily_kwh = parameters.get("daily_kwh", 30)
                backup_days = parameters.get("backup_days", 1.0)
                depth_of_discharge = parameters.get("depth_of_discharge", 0.80)
                backup_percentage = parameters.get("backup_percentage", 100) / 100

                energy_needed = daily_kwh * backup_days * backup_percentage
                battery_size_kwh = energy_needed / depth_of_discharge

                result = {
                    "battery_size_kwh": round(battery_size_kwh, 1),
                    "usable_capacity_kwh": round(energy_needed, 1)
                }
                explanation = f"To backup {backup_percentage:.0%} of {daily_kwh} kWh daily usage for {backup_days} days at {depth_of_discharge:.0%} DoD, you need approximately {battery_size_kwh:.1f} kWh battery capacity."
                assumptions = [
                    f"Daily usage: {daily_kwh} kWh",
                    f"Backup duration: {backup_days} days",
                    f"Depth of discharge: {depth_of_discharge:.0%}",
                    f"Backup percentage: {backup_percentage:.0%}"
                ]
                recommendations = [
                    "Consider lithium-ion for best cycle life",
                    "Check if your area has time-of-use rates for additional savings"
                ]

            response_data = {"result": result}
            if include_explanation:
                response_data["explanation"] = explanation
            if assumptions:
                response_data["assumptions"] = assumptions
            if recommendations:
                response_data["recommendations"] = recommendations

            return APIResponse(success=True, data=response_data)

        except Exception as e:
            return APIResponse(success=False, error=str(e))

    def analyze_image(
        self,
        image_data: bytes,
        analysis_type: str = "general",
        include_recommendations: bool = True
    ) -> APIResponse:
        """
        Analyze a solar panel image.

        Args:
            image_data: Image bytes
            analysis_type: Type of analysis (general, defect_detection, shading, layout)
            include_recommendations: Whether to include recommendations

        Returns:
            APIResponse with analysis results
        """
        try:
            # Mock image analysis results
            # In production, this would integrate with a vision AI model

            if analysis_type == "defect_detection":
                analysis_result = {
                    "confidence_score": 0.85,
                    "analysis": "Image analysis complete. The solar panels appear to be in generally good condition with minor observations noted.",
                    "detected_elements": [
                        {"type": "Solar Panel", "confidence": 0.95},
                        {"type": "Mounting Structure", "confidence": 0.88},
                        {"type": "Wiring", "confidence": 0.72}
                    ],
                    "issues_found": [
                        {
                            "description": "Minor dust accumulation detected on panel surface - consider cleaning",
                            "severity": "info"
                        },
                        {
                            "description": "Potential micro-crack in cell (low confidence) - monitor for changes",
                            "severity": "warning"
                        }
                    ],
                    "recommendations": [
                        "Schedule routine cleaning to maintain optimal efficiency",
                        "Monitor the flagged area during next inspection",
                        "Consider thermal imaging for comprehensive defect detection"
                    ] if include_recommendations else []
                }
            elif analysis_type == "shading":
                analysis_result = {
                    "confidence_score": 0.82,
                    "analysis": "Shading analysis indicates minimal obstruction. The array receives good solar exposure during peak hours.",
                    "detected_elements": [
                        {"type": "Solar Array", "confidence": 0.93},
                        {"type": "Tree (nearby)", "confidence": 0.65},
                        {"type": "Building Edge", "confidence": 0.78}
                    ],
                    "issues_found": [
                        {
                            "description": "Partial shading detected in morning hours from nearby vegetation",
                            "severity": "warning"
                        }
                    ],
                    "recommendations": [
                        "Consider tree trimming to reduce morning shading",
                        "Microinverters or optimizers could mitigate shading losses",
                        "Annual shading analysis recommended as vegetation grows"
                    ] if include_recommendations else []
                }
            elif analysis_type == "layout":
                analysis_result = {
                    "confidence_score": 0.88,
                    "analysis": "Array layout analysis shows efficient use of available roof space with proper spacing for maintenance access.",
                    "detected_elements": [
                        {"type": "Solar Panel (count: 20)", "confidence": 0.94},
                        {"type": "Inverter", "confidence": 0.76},
                        {"type": "Roof Structure", "confidence": 0.91}
                    ],
                    "issues_found": [],
                    "recommendations": [
                        "Layout appears optimized for the available space",
                        "Consider expansion if additional roof area becomes available",
                        "Ensure all permits reflect current installation configuration"
                    ] if include_recommendations else []
                }
            else:  # general
                analysis_result = {
                    "confidence_score": 0.87,
                    "analysis": "General analysis of the solar installation shows a well-maintained system. The panels are properly mounted and appear to be functioning normally based on visual inspection.",
                    "detected_elements": [
                        {"type": "Monocrystalline Solar Panel", "confidence": 0.91},
                        {"type": "Aluminum Frame", "confidence": 0.89},
                        {"type": "Roof Mount System", "confidence": 0.85}
                    ],
                    "issues_found": [
                        {
                            "description": "Normal wear and aging observed - consistent with system age",
                            "severity": "info"
                        }
                    ],
                    "recommendations": [
                        "Continue regular visual inspections",
                        "Schedule professional maintenance annually",
                        "Monitor system performance through your monitoring portal"
                    ] if include_recommendations else []
                }

            return APIResponse(success=True, data=analysis_result)

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
