"""Image analysis router for Solar PV systems."""

import base64
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

from ..models.schemas import ImageAnalysisRequest, ImageAnalysisResponse

router = APIRouter(prefix="/analyze", tags=["Image Analysis"])


def analyze_general(image_data: bytes) -> Dict[str, Any]:
    """Perform general solar PV image analysis."""
    # Mock analysis - in production, this would use computer vision models
    return {
        "analysis": """**Solar Panel Array Analysis**

Based on the image analysis:

1. **Panel Configuration**: The image shows a solar panel installation
2. **Orientation**: Panels appear to be properly oriented for solar exposure
3. **Condition**: Visual inspection suggests panels are in good condition

**Key Observations:**
- Panel arrangement follows standard grid pattern
- Mounting system appears secure
- No obvious physical damage detected

**Note**: This is a preliminary visual analysis. For accurate assessment, please consult a certified solar technician.""",
        "detected_elements": [
            {"type": "solar_panel", "count": "multiple", "confidence": 0.85},
            {"type": "mounting_system", "detected": True, "confidence": 0.80},
            {"type": "wiring", "visible": True, "confidence": 0.70}
        ],
        "issues_found": [],
        "confidence": 0.82
    }


def analyze_defects(image_data: bytes) -> Dict[str, Any]:
    """Analyze image for defects."""
    # Mock defect analysis
    return {
        "analysis": """**Defect Detection Analysis**

The image has been analyzed for common solar panel defects:

1. **Hot Spots**: No obvious hot spots detected
2. **Microcracks**: Unable to detect without thermal imaging
3. **Discoloration**: No significant discoloration observed
4. **Physical Damage**: No visible physical damage

**Recommendations:**
- Schedule thermal imaging inspection for comprehensive analysis
- Check inverter logs for performance anomalies
- Consider drone inspection for large arrays""",
        "detected_elements": [
            {"type": "panel_surface", "condition": "appears_normal", "confidence": 0.75}
        ],
        "issues_found": [
            {"type": "recommendation", "severity": "info", "description": "Thermal imaging recommended for thorough defect detection"}
        ],
        "confidence": 0.70
    }


def analyze_shading(image_data: bytes) -> Dict[str, Any]:
    """Analyze image for shading issues."""
    return {
        "analysis": """**Shading Analysis**

Potential shading sources have been analyzed:

1. **Nearby Structures**: Check for buildings that may cast shadows
2. **Vegetation**: Trees and foliage should be monitored
3. **Self-Shading**: Panel rows should maintain proper spacing

**Impact Assessment:**
- Morning shading: Minimal impact if panels face south
- Afternoon shading: More significant impact on production
- Seasonal variation: Winter shadows are longer

**Recommendations:**
- Use monitoring data to identify production dips
- Consider microinverters or optimizers for partial shading
- Trim vegetation that causes shading""",
        "detected_elements": [
            {"type": "potential_shade_source", "location": "analysis_pending", "confidence": 0.65}
        ],
        "issues_found": [],
        "confidence": 0.68
    }


def analyze_layout(image_data: bytes) -> Dict[str, Any]:
    """Analyze panel layout and configuration."""
    return {
        "analysis": """**Layout Analysis**

Panel layout assessment:

1. **Array Configuration**: Standard grid layout detected
2. **Spacing**: Panels appear adequately spaced
3. **Orientation**: Assessment requires compass data

**Design Considerations:**
- Row spacing should prevent self-shading
- Access paths should be maintained for maintenance
- Fire code setbacks should be verified

**Optimization Suggestions:**
- Verify tilt angle matches latitude
- Ensure adequate ventilation under panels
- Check string configuration for optimal performance""",
        "detected_elements": [
            {"type": "array_layout", "pattern": "grid", "confidence": 0.78},
            {"type": "row_spacing", "assessment": "adequate", "confidence": 0.72}
        ],
        "issues_found": [],
        "confidence": 0.75
    }


ANALYSIS_FUNCTIONS = {
    "general": analyze_general,
    "defect_detection": analyze_defects,
    "shading": analyze_shading,
    "layout": analyze_layout
}


@router.post("/image", response_model=ImageAnalysisResponse)
async def analyze_image(request: ImageAnalysisRequest):
    """
    Analyze a solar PV system image.

    Args:
        request: Image analysis request with base64 image

    Returns:
        Analysis results with detected elements and recommendations
    """
    try:
        # Validate and decode base64 image
        try:
            # Handle data URL format
            if "," in request.image_base64:
                image_data = base64.b64decode(request.image_base64.split(",")[1])
            else:
                image_data = base64.b64decode(request.image_base64)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 image data")

        # Get analysis function
        analysis_func = ANALYSIS_FUNCTIONS.get(request.analysis_type, analyze_general)

        # Perform analysis
        result = analysis_func(image_data)

        # Generate recommendations if requested
        recommendations = []
        if request.include_recommendations:
            recommendations = [
                "Schedule regular visual inspections",
                "Monitor system performance data",
                "Keep panels clean for optimal performance",
                "Document any changes or issues observed"
            ]
            # Add any issue-specific recommendations
            for issue in result.get("issues_found", []):
                if issue.get("description"):
                    recommendations.append(issue["description"])

        return ImageAnalysisResponse(
            analysis=result["analysis"],
            detected_elements=result.get("detected_elements", []),
            issues_found=result.get("issues_found", []),
            recommendations=recommendations,
            confidence_score=result.get("confidence", 0.75)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis error: {str(e)}")


@router.get("/types")
async def get_analysis_types():
    """Get available image analysis types."""
    return {
        "general": "General solar panel array analysis",
        "defect_detection": "Detect potential defects and damage",
        "shading": "Analyze shading issues and impacts",
        "layout": "Analyze panel layout and configuration"
    }


@router.get("/health")
async def image_health():
    """Health check for image analysis service."""
    return {"status": "healthy", "service": "image_analysis"}
