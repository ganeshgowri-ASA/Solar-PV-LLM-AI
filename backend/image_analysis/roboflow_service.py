"""
Roboflow Integration Service for Solar Panel Image Analysis
Provides VI (Visual Inspection), EL (Electroluminescence), and IR (Infrared) analysis.

This is a placeholder module - full Roboflow integration coming soon.
"""

import os
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required if env vars are set directly


class AnalysisType(Enum):
    """Types of solar panel image analysis"""
    VISUAL_INSPECTION = "vi"  # Visual defect detection
    ELECTROLUMINESCENCE = "el"  # EL imaging analysis
    INFRARED = "ir"  # Thermal/IR imaging analysis
    GENERAL = "general"  # General panel detection


@dataclass
class DefectDetection:
    """Detected defect information"""
    defect_type: str
    confidence: float
    location: Dict[str, float]  # x, y, width, height
    severity: str  # low, medium, high, critical
    description: str


@dataclass
class ImageAnalysisResult:
    """Result of image analysis"""
    success: bool
    analysis_type: AnalysisType
    detected_panels: int = 0
    defects: List[DefectDetection] = field(default_factory=list)
    confidence: float = 0.0
    processing_time_ms: int = 0
    recommendations: List[str] = field(default_factory=list)
    raw_response: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class RoboflowService:
    """
    Roboflow integration service for solar panel image analysis.

    Supports:
    - Visual Inspection (VI): Detect visible defects, damage, soiling
    - Electroluminescence (EL): Analyze EL images for cell defects
    - Infrared (IR): Thermal analysis for hot spots and performance issues

    Note: This is a placeholder implementation. Full Roboflow integration requires:
    1. Roboflow API key
    2. Trained model for solar panel defect detection
    3. Model deployment on Roboflow
    """

    # Defect type classifications
    DEFECT_TYPES = {
        "vi": [
            "cracking", "delamination", "discoloration", "soiling",
            "hotspot", "snail_trail", "broken_glass", "corrosion"
        ],
        "el": [
            "cell_crack", "inactive_cell", "finger_interruption",
            "shunt", "microcracks", "cell_gap"
        ],
        "ir": [
            "hotspot", "string_failure", "bypass_diode_failure",
            "connection_issue", "cell_mismatch", "soiling"
        ]
    }

    def __init__(self):
        """Initialize Roboflow service"""
        self.api_key = os.getenv("ROBOFLOW_API_KEY")
        self.workspace = os.getenv("ROBOFLOW_WORKSPACE", "solar-pv-analysis")
        self.project = os.getenv("ROBOFLOW_PROJECT", "pv-defect-detection")
        self.version = os.getenv("ROBOFLOW_MODEL_VERSION", "1")
        self._client = None
        self._model = None

    @property
    def is_configured(self) -> bool:
        """Check if Roboflow is properly configured"""
        return self.api_key is not None

    def _get_client(self):
        """
        Initialize Roboflow client.

        Note: Requires `pip install roboflow`
        """
        if self._client is None:
            if not self.api_key:
                return None

            try:
                from roboflow import Roboflow
                self._client = Roboflow(api_key=self.api_key)
            except ImportError:
                print("Warning: roboflow package not installed. Install with: pip install roboflow")
                return None

        return self._client

    def _get_model(self):
        """Get the trained model for inference"""
        if self._model is None:
            client = self._get_client()
            if client:
                try:
                    project = client.workspace(self.workspace).project(self.project)
                    self._model = project.version(self.version).model
                except Exception as e:
                    print(f"Error loading model: {e}")
                    return None
        return self._model

    def analyze_image(
        self,
        image_path: str,
        analysis_type: AnalysisType = AnalysisType.GENERAL,
        confidence_threshold: float = 0.4
    ) -> ImageAnalysisResult:
        """
        Analyze a solar panel image for defects.

        Args:
            image_path: Path to the image file
            analysis_type: Type of analysis to perform
            confidence_threshold: Minimum confidence for detections

        Returns:
            ImageAnalysisResult with defects and recommendations
        """
        # Check if Roboflow is configured
        if not self.is_configured:
            return ImageAnalysisResult(
                success=False,
                analysis_type=analysis_type,
                error="Roboflow not configured. Set ROBOFLOW_API_KEY in environment.",
                recommendations=[
                    "Configure ROBOFLOW_API_KEY in your .env file",
                    "Set up a Roboflow project for solar panel analysis",
                    "Train or use a pre-trained model for defect detection"
                ]
            )

        model = self._get_model()
        if not model:
            return self._get_placeholder_result(analysis_type)

        try:
            # Perform inference
            prediction = model.predict(image_path, confidence=confidence_threshold)
            predictions = prediction.json()

            # Parse detections
            defects = self._parse_detections(predictions, analysis_type)
            panel_count = self._count_panels(predictions)

            return ImageAnalysisResult(
                success=True,
                analysis_type=analysis_type,
                detected_panels=panel_count,
                defects=defects,
                confidence=self._calculate_avg_confidence(defects),
                recommendations=self._generate_recommendations(defects),
                raw_response=predictions
            )

        except Exception as e:
            return ImageAnalysisResult(
                success=False,
                analysis_type=analysis_type,
                error=str(e)
            )

    def analyze_image_bytes(
        self,
        image_data: bytes,
        analysis_type: AnalysisType = AnalysisType.GENERAL,
        confidence_threshold: float = 0.4
    ) -> ImageAnalysisResult:
        """
        Analyze image from bytes data.

        Args:
            image_data: Raw image bytes
            analysis_type: Type of analysis
            confidence_threshold: Minimum confidence

        Returns:
            ImageAnalysisResult
        """
        # Placeholder - actual implementation would use Roboflow's base64 inference
        if not self.is_configured:
            return self._get_placeholder_result(analysis_type)

        return self._get_placeholder_result(analysis_type)

    def _parse_detections(
        self,
        predictions: Dict[str, Any],
        analysis_type: AnalysisType
    ) -> List[DefectDetection]:
        """Parse Roboflow predictions into DefectDetection objects"""
        defects = []
        valid_defects = self.DEFECT_TYPES.get(analysis_type.value, [])

        for pred in predictions.get("predictions", []):
            defect_class = pred.get("class", "").lower()

            # Skip non-defect detections (like panel itself)
            if defect_class not in valid_defects and defect_class != "defect":
                continue

            defects.append(DefectDetection(
                defect_type=defect_class,
                confidence=pred.get("confidence", 0.0),
                location={
                    "x": pred.get("x", 0),
                    "y": pred.get("y", 0),
                    "width": pred.get("width", 0),
                    "height": pred.get("height", 0)
                },
                severity=self._determine_severity(pred.get("confidence", 0)),
                description=self._get_defect_description(defect_class)
            ))

        return defects

    def _count_panels(self, predictions: Dict[str, Any]) -> int:
        """Count detected solar panels"""
        panel_count = 0
        for pred in predictions.get("predictions", []):
            if pred.get("class", "").lower() in ["panel", "solar_panel", "module"]:
                panel_count += 1
        return max(1, panel_count)  # Assume at least 1 panel if analyzing

    def _determine_severity(self, confidence: float) -> str:
        """Determine defect severity based on confidence"""
        if confidence >= 0.9:
            return "critical"
        elif confidence >= 0.7:
            return "high"
        elif confidence >= 0.5:
            return "medium"
        else:
            return "low"

    def _get_defect_description(self, defect_type: str) -> str:
        """Get human-readable description for defect type"""
        descriptions = {
            "cracking": "Visible crack in the panel surface or cells",
            "delamination": "Separation of panel layers causing performance loss",
            "discoloration": "Color change indicating degradation or damage",
            "soiling": "Dirt, debris, or biological growth on panel surface",
            "hotspot": "Localized overheating due to cell damage or shading",
            "snail_trail": "Silver discoloration pattern indicating moisture ingress",
            "broken_glass": "Damaged front glass requiring immediate attention",
            "corrosion": "Oxidation of metallic components",
            "cell_crack": "Microscopic crack in photovoltaic cell",
            "inactive_cell": "Cell not producing power",
            "finger_interruption": "Broken electrical contacts within cell",
            "shunt": "Short circuit within cell reducing efficiency",
            "microcracks": "Fine cracks not visible to naked eye",
            "cell_gap": "Abnormal spacing between cells",
            "string_failure": "Complete string of cells not functioning",
            "bypass_diode_failure": "Failed bypass diode causing hotspots",
            "connection_issue": "Poor electrical connection in wiring",
            "cell_mismatch": "Cells with different performance characteristics"
        }
        return descriptions.get(defect_type, f"Detected {defect_type} requiring inspection")

    def _calculate_avg_confidence(self, defects: List[DefectDetection]) -> float:
        """Calculate average confidence across detections"""
        if not defects:
            return 0.0
        return sum(d.confidence for d in defects) / len(defects)

    def _generate_recommendations(self, defects: List[DefectDetection]) -> List[str]:
        """Generate maintenance recommendations based on defects"""
        recommendations = []

        if not defects:
            recommendations.append("No defects detected - continue regular maintenance schedule")
            return recommendations

        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for defect in defects:
            severity_counts[defect.severity] += 1

        if severity_counts["critical"] > 0:
            recommendations.append("URGENT: Critical defects require immediate professional inspection")

        if severity_counts["high"] > 0:
            recommendations.append("Schedule professional inspection within 1-2 weeks")

        if any(d.defect_type == "hotspot" for d in defects):
            recommendations.append("Check for shading sources and clean panel surface")

        if any(d.defect_type in ["soiling", "discoloration"] for d in defects):
            recommendations.append("Consider professional cleaning service")

        if any(d.defect_type in ["cracking", "broken_glass"] for d in defects):
            recommendations.append("Panel replacement may be necessary - consult installer")

        return recommendations

    def _get_placeholder_result(self, analysis_type: AnalysisType) -> ImageAnalysisResult:
        """Return placeholder result when Roboflow is not available"""
        return ImageAnalysisResult(
            success=False,
            analysis_type=analysis_type,
            error="Roboflow integration pending",
            recommendations=[
                "Roboflow VI/EL/IR analysis integration in progress",
                "Configure ROBOFLOW_API_KEY for full functionality",
                "Manual inspection recommended in the meantime"
            ]
        )


# Singleton service instance
_service_instance: Optional[RoboflowService] = None


def get_roboflow_service() -> RoboflowService:
    """
    Get or create Roboflow service singleton.

    Returns:
        RoboflowService instance
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = RoboflowService()
    return _service_instance
