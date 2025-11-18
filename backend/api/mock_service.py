"""
Mock API service for Solar PV LLM AI System
Simulates backend responses for frontend development
"""
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd


class MockAPIService:
    """Mock API service to simulate backend responses"""

    def __init__(self):
        self.standards_db = self._init_standards_db()
        self.chat_history = []

    def _init_standards_db(self) -> List[Dict[str, Any]]:
        """Initialize mock standards database"""
        return [
            {
                "id": "iec-61215",
                "title": "IEC 61215 - Crystalline Silicon PV Module Testing",
                "category": "Module Testing",
                "description": "Terrestrial photovoltaic (PV) modules - Design qualification and type approval",
                "sections": [
                    "General Requirements",
                    "Visual Inspection",
                    "Maximum Power Determination",
                    "Insulation Test",
                    "Temperature Coefficient Measurement",
                    "NOCT Measurement",
                    "Performance at Low Irradiance",
                    "Outdoor Exposure Test",
                    "Hot-Spot Endurance Test",
                    "UV Preconditioning Test",
                    "Thermal Cycling Test",
                    "Humidity Freeze Test",
                    "Damp Heat Test",
                    "Robustness of Terminations Test",
                    "Wet Leakage Current Test",
                    "Mechanical Load Test",
                    "Hail Test",
                    "Bypass Diode Thermal Test",
                ],
                "test_count": 18,
                "difficulty": "Advanced",
            },
            {
                "id": "iec-61730",
                "title": "IEC 61730 - PV Module Safety Qualification",
                "category": "Safety",
                "description": "Photovoltaic (PV) module safety qualification",
                "sections": [
                    "General Requirements",
                    "Construction Requirements",
                    "Mechanical Stress Test",
                    "Electrical Safety Test",
                    "Fire Safety Test",
                    "Environmental Test",
                ],
                "test_count": 6,
                "difficulty": "Intermediate",
            },
            {
                "id": "iec-61853",
                "title": "IEC 61853 - PV Module Performance Testing",
                "category": "Performance",
                "description": "Photovoltaic (PV) module performance testing and energy rating",
                "sections": [
                    "Irradiance and Temperature Performance",
                    "Spectral Response",
                    "Incidence Angle Response",
                    "Operating Temperature",
                    "Energy Rating",
                ],
                "test_count": 5,
                "difficulty": "Intermediate",
            },
            {
                "id": "iec-62446",
                "title": "IEC 62446 - Grid Connected PV Systems",
                "category": "Systems",
                "description": "Grid connected photovoltaic systems - Minimum requirements for system documentation, commissioning tests and inspection",
                "sections": [
                    "Documentation Requirements",
                    "Commissioning Tests",
                    "Inspection Procedures",
                    "Performance Verification",
                ],
                "test_count": 4,
                "difficulty": "Beginner",
            },
            {
                "id": "iec-60904",
                "title": "IEC 60904 - PV Device Measurements",
                "category": "Measurements",
                "description": "Photovoltaic devices - Measurement procedures",
                "sections": [
                    "Measurement of Current-Voltage Characteristics",
                    "Reference Devices Calibration",
                    "Standard Test Conditions",
                    "Temperature and Irradiance Corrections",
                ],
                "test_count": 4,
                "difficulty": "Intermediate",
            },
        ]

    def chat_completion(
        self, message: str, include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Simulate chat completion with RAG
        """
        time.sleep(0.5)  # Simulate API delay

        # Generate mock response based on keywords
        response_text = self._generate_mock_response(message)

        # Generate mock sources
        sources = []
        if include_sources:
            sources = self._generate_mock_sources(message)

        return {
            "content": response_text,
            "sources": sources,
            "timestamp": datetime.now().isoformat(),
            "model": "gpt-4-turbo-preview",
        }

    def _generate_mock_response(self, message: str) -> str:
        """Generate contextual mock response"""
        message_lower = message.lower()

        if "test" in message_lower or "testing" in message_lower:
            return """Based on IEC standards, solar PV module testing involves several key procedures:

1. **Visual Inspection**: Check for physical defects, proper labeling, and construction quality
2. **Electrical Performance**: Measure I-V characteristics, maximum power, and efficiency under standard test conditions (STC: 1000 W/m², 25°C, AM 1.5)
3. **Safety Tests**: Insulation resistance, wet leakage current, and ground continuity
4. **Environmental Tests**:
   - Thermal cycling (-40°C to +85°C)
   - Humidity freeze
   - Damp heat (85°C/85% RH for 1000 hours)
   - UV preconditioning
5. **Mechanical Tests**: Static and dynamic mechanical load testing, hail impact test
6. **Hot-spot endurance**: Verify bypass diode protection

These tests ensure modules meet safety, reliability, and performance requirements per IEC 61215 and IEC 61730 standards."""

        elif "efficiency" in message_lower or "calculate" in message_lower:
            return """Solar PV efficiency can be calculated using:

**Module Efficiency = (Pmax / (A × G)) × 100%**

Where:
- Pmax = Maximum power output (W)
- A = Module area (m²)
- G = Irradiance (W/m²)

For system-level calculations:
- **Performance Ratio (PR)** = Actual Energy / Theoretical Energy
- **Capacity Factor** = Actual Output / Rated Capacity
- **Energy Yield** = Irradiation × System Size × PR

Typical crystalline silicon module efficiency ranges from 18-22%, while system efficiency is typically 75-85% due to losses from inverters, wiring, shading, and temperature effects."""

        elif "standard" in message_lower or "iec" in message_lower:
            return """Key IEC standards for solar PV systems include:

**Module Level:**
- **IEC 61215**: Design qualification and type approval for crystalline silicon modules
- **IEC 61730**: Module safety qualification (electrical and fire safety)
- **IEC 61853**: Module performance testing and energy rating

**System Level:**
- **IEC 62446**: Grid-connected system documentation and commissioning
- **IEC 61724**: PV system performance monitoring
- **IEC 62109**: Safety of power converters in PV systems

**Measurement Standards:**
- **IEC 60904**: Photovoltaic device measurement procedures
- **IEC 61727**: Characteristics of grid-connected inverters

Each standard ensures safety, reliability, and performance requirements are met throughout the product lifecycle."""

        elif "safety" in message_lower:
            return """PV module safety requirements per IEC 61730 include:

**Construction Requirements:**
- Adequate insulation and isolation
- Proper grounding provisions
- Fire-resistant materials (Class A or B)
- Secure terminations and connections

**Electrical Safety:**
- Insulation resistance > 40 MΩ
- Wet leakage current < 1 μA/V
- Voltage rating appropriate for system design
- Proper protection against reverse current

**Fire Safety:**
- Fire classification testing
- Spread of flame testing
- Material flammability assessment

**Environmental Protection:**
- IP67 or better for junction boxes
- Protection against moisture ingress
- UV and temperature resistance

Regular safety inspections and compliance testing ensure long-term safe operation."""

        else:
            return """I can help you with various aspects of solar PV systems, including:

- IEC standards and compliance requirements
- Module testing procedures and methodologies
- Performance calculations and system design
- Safety requirements and best practices
- Energy yield estimation and optimization
- Image analysis of PV installations
- Technical troubleshooting and recommendations

Please feel free to ask specific questions about any of these topics, and I'll provide detailed, citation-backed answers based on industry standards and best practices."""

    def _generate_mock_sources(self, message: str) -> List[Dict[str, Any]]:
        """Generate mock source citations"""
        sources = []

        # Select relevant standards based on message content
        relevant_standards = [
            s for s in self.standards_db
            if any(word in message.lower() for word in s["title"].lower().split())
        ]

        if not relevant_standards:
            relevant_standards = random.sample(self.standards_db, min(3, len(self.standards_db)))

        for std in relevant_standards[:3]:
            sources.append({
                "title": std["title"],
                "excerpt": f"{std['description']}... This standard covers {std['test_count']} key test procedures.",
                "page": random.randint(10, 150),
                "section": random.choice(std["sections"]),
                "relevance_score": random.uniform(0.75, 0.95),
            })

        return sources

    def search_standards(
        self,
        query: str = "",
        categories: Optional[List[str]] = None,
        difficulty: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Search standards database with filters"""
        time.sleep(0.3)

        results = self.standards_db.copy()

        # Apply query filter
        if query:
            results = [
                s for s in results
                if query.lower() in s["title"].lower()
                or query.lower() in s["description"].lower()
            ]

        # Apply category filter
        if categories:
            results = [s for s in results if s["category"] in categories]

        # Apply difficulty filter
        if difficulty:
            results = [s for s in results if s["difficulty"] in difficulty]

        return results

    def get_standard_detail(self, standard_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a standard"""
        time.sleep(0.2)

        for std in self.standards_db:
            if std["id"] == standard_id:
                # Add additional details
                std_detail = std.copy()
                std_detail["last_updated"] = "2023-06-15"
                std_detail["version"] = "Edition 3.1"
                std_detail["status"] = "Active"
                std_detail["related_standards"] = [
                    s["id"] for s in self.standards_db if s["id"] != standard_id
                ][:3]
                return std_detail

        return None

    def analyze_image(self, image_file) -> Dict[str, Any]:
        """Simulate image analysis"""
        time.sleep(1.5)

        return {
            "status": "success",
            "analysis": {
                "module_type": "Monocrystalline Silicon",
                "detected_defects": [
                    {
                        "type": "Micro-crack",
                        "severity": "Medium",
                        "location": "Cell A5",
                        "confidence": 0.87,
                    },
                    {
                        "type": "Hot-spot",
                        "severity": "Low",
                        "location": "Cell B3",
                        "confidence": 0.72,
                    },
                ],
                "overall_health": "Good",
                "recommendations": [
                    "Monitor micro-crack in Cell A5 for potential degradation",
                    "Verify bypass diode functionality for hot-spot in Cell B3",
                    "Schedule follow-up inspection in 6 months",
                ],
                "estimated_power_loss": "2.3%",
            },
            "timestamp": datetime.now().isoformat(),
        }

    def calculate_energy_yield(
        self,
        system_size_kw: float,
        location_irradiance: float,
        performance_ratio: float = 0.8,
    ) -> Dict[str, Any]:
        """Calculate energy yield"""
        daily_energy = system_size_kw * location_irradiance * performance_ratio
        annual_energy = daily_energy * 365

        return {
            "daily_energy_kwh": round(daily_energy, 2),
            "monthly_energy_kwh": round(daily_energy * 30, 2),
            "annual_energy_kwh": round(annual_energy, 2),
            "annual_energy_mwh": round(annual_energy / 1000, 2),
            "co2_offset_kg": round(annual_energy * 0.5, 2),  # Approx 0.5 kg CO2/kWh
        }

    def calculate_system_sizing(
        self,
        daily_consumption_kwh: float,
        peak_sun_hours: float,
        system_efficiency: float = 0.8,
    ) -> Dict[str, Any]:
        """Calculate system sizing"""
        required_system_size = (daily_consumption_kwh / peak_sun_hours) / system_efficiency

        # Assume 400W panels
        panel_wattage = 400
        num_panels = int(required_system_size * 1000 / panel_wattage) + 1

        return {
            "required_system_size_kw": round(required_system_size, 2),
            "recommended_panels": num_panels,
            "panel_wattage": panel_wattage,
            "total_system_size_kw": round((num_panels * panel_wattage) / 1000, 2),
            "estimated_roof_area_m2": round(num_panels * 2, 2),  # ~2 m² per panel
        }

    def calculate_roi(
        self,
        system_cost: float,
        annual_savings: float,
        electricity_rate_increase: float = 0.03,
    ) -> Dict[str, Any]:
        """Calculate ROI"""
        years_to_payback = system_cost / annual_savings

        total_savings_25_years = sum(
            annual_savings * ((1 + electricity_rate_increase) ** year)
            for year in range(25)
        )

        roi_percentage = ((total_savings_25_years - system_cost) / system_cost) * 100

        return {
            "payback_period_years": round(years_to_payback, 1),
            "total_savings_25_years": round(total_savings_25_years, 2),
            "roi_percentage": round(roi_percentage, 1),
            "net_profit_25_years": round(total_savings_25_years - system_cost, 2),
        }

    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get dashboard metrics"""
        return {
            "system_health": {
                "status": "Healthy",
                "uptime_percentage": 99.7,
                "active_queries": random.randint(10, 50),
                "response_time_ms": random.randint(150, 350),
            },
            "usage_stats": {
                "total_queries": random.randint(1000, 5000),
                "successful_queries": random.randint(900, 4800),
                "failed_queries": random.randint(10, 50),
                "avg_response_time": random.randint(200, 400),
            },
            "knowledge_base": {
                "total_documents": 1247,
                "indexed_standards": len(self.standards_db),
                "last_updated": datetime.now().isoformat(),
                "index_size_mb": random.randint(500, 1500),
            },
            "recent_activity": self._generate_recent_activity(),
        }

    def _generate_recent_activity(self) -> List[Dict[str, Any]]:
        """Generate mock recent activity"""
        activities = []
        activity_types = [
            "Query answered",
            "Document indexed",
            "Standard updated",
            "Image analyzed",
            "Calculation performed",
        ]

        for i in range(10):
            activities.append({
                "type": random.choice(activity_types),
                "timestamp": (datetime.now() - timedelta(minutes=random.randint(1, 120))).isoformat(),
                "status": random.choice(["success", "success", "success", "warning"]),
            })

        return activities

    def get_time_series_data(self, days: int = 30) -> pd.DataFrame:
        """Generate time series data for charts"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq="D")
        data = {
            "date": dates,
            "queries": [random.randint(50, 200) for _ in range(days)],
            "response_time": [random.randint(150, 400) for _ in range(days)],
            "success_rate": [random.uniform(95, 100) for _ in range(days)],
        }
        return pd.DataFrame(data)


# Global instance
mock_api = MockAPIService()
