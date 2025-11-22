"""
Image analysis endpoints for solar panel defect detection.
"""
import time
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from loguru import logger

from app.models.schemas import ImageAnalysisRequest, ImageAnalysisResponse
from app.services.image_analyzer import image_analyzer
from app.core.security import verify_api_key

router = APIRouter(prefix="/image-analysis", tags=["Image Analysis"])


@router.post("/analyze", response_model=ImageAnalysisResponse)
async def analyze_image(
    request: ImageAnalysisRequest,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Analyze solar panel image for defects.

    Performs computer vision analysis to detect:
    - Hotspots
    - Cracks and micro-cracks
    - Delamination
    - Discoloration
    - Soiling
    - PID (Potential Induced Degradation)
    - Bypass diode failures

    **Input:**
    - image_base64: Base64 encoded image
    - OR image_url: URL to image (future implementation)
    - analysis_type: Type of analysis (defect_detection, thermal_analysis)

    **Returns:**
    - List of detected defects with confidence scores
    - Overall health score (0-100)
    - Maintenance recommendations
    - Image dimensions
    """
    start_time = time.time()

    try:
        logger.info(f"Analyzing image for defects ({request.analysis_type})")

        if not request.image_base64 and not request.image_url:
            raise HTTPException(
                status_code=400,
                detail="Either image_base64 or image_url must be provided"
            )

        # Analyze image
        defects, health_score, dimensions, recommendations = image_analyzer.analyze_image(
            image_base64=request.image_base64
        )

        processing_time = time.time() - start_time

        response = ImageAnalysisResponse(
            defects=defects,
            overall_health_score=health_score,
            processing_time=round(processing_time, 3),
            image_dimensions=dimensions,
            recommendations=recommendations
        )

        logger.info(
            f"Analysis complete: {len(defects)} defects, "
            f"health score: {health_score:.1f}, "
            f"time: {processing_time:.2f}s"
        )

        return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-and-analyze", response_model=ImageAnalysisResponse)
async def upload_and_analyze(
    file: UploadFile = File(...),
    authenticated: bool = Depends(verify_api_key)
):
    """
    Upload and analyze image file.

    Alternative endpoint that accepts file upload instead of base64.

    **Supported formats:**
    - JPEG/JPG
    - PNG
    - TIFF

    **Returns:**
    - Same as /analyze endpoint
    """
    start_time = time.time()

    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/tiff"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}"
            )

        # Read file
        logger.info(f"Uploaded file: {file.filename} ({file.content_type})")
        contents = await file.read()

        # Convert to base64
        import base64
        image_base64 = base64.b64encode(contents).decode('utf-8')

        # Analyze
        defects, health_score, dimensions, recommendations = image_analyzer.analyze_image(
            image_base64=image_base64
        )

        processing_time = time.time() - start_time

        response = ImageAnalysisResponse(
            defects=defects,
            overall_health_score=health_score,
            processing_time=round(processing_time, 3),
            image_dimensions=dimensions,
            recommendations=recommendations
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing uploaded image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supported-defects")
async def get_supported_defects(
    authenticated: bool = Depends(verify_api_key)
):
    """
    Get list of supported defect types.

    **Returns:**
    - List of defect types that can be detected
    - Description for each type
    """
    from app.models.schemas import DefectType

    defect_info = {
        DefectType.HOTSPOT: {
            "name": "Hotspot",
            "description": "Elevated temperature areas indicating electrical issues",
            "severity": "High - can lead to fire hazard"
        },
        DefectType.CRACK: {
            "name": "Crack/Micro-crack",
            "description": "Physical cracks in solar cells",
            "severity": "Medium-High - affects power output"
        },
        DefectType.DELAMINATION: {
            "name": "Delamination",
            "description": "Separation of panel layers",
            "severity": "High - leads to moisture ingress"
        },
        DefectType.DISCOLORATION: {
            "name": "Discoloration",
            "description": "UV-induced or EVA degradation",
            "severity": "Low-Medium - cosmetic to functional"
        },
        DefectType.SOILING: {
            "name": "Soiling",
            "description": "Dirt, dust, or debris accumulation",
            "severity": "Low - easily cleaned"
        },
        DefectType.SNAIL_TRAIL: {
            "name": "Snail Trail",
            "description": "Discoloration pattern from micro-cracks",
            "severity": "Medium - indicates cell damage"
        },
        DefectType.PID: {
            "name": "PID (Potential Induced Degradation)",
            "description": "Voltage-induced performance degradation",
            "severity": "High - significant power loss"
        },
        DefectType.BYPASS_DIODE_FAILURE: {
            "name": "Bypass Diode Failure",
            "description": "Failed bypass diode causing hotspots",
            "severity": "High - fire hazard"
        }
    }

    return {
        "supported_defects": len(defect_info),
        "defect_types": defect_info
    }
