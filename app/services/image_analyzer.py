"""
Image Analysis Service for Solar Panel Defect Detection.
Uses computer vision and deep learning for defect identification.
"""
import io
import base64
from typing import List, Dict, Tuple
from pathlib import Path
import numpy as np
from PIL import Image
import cv2
from loguru import logger

from app.core.config import settings
from app.models.schemas import DetectedDefect, DefectType


class ImageAnalyzer:
    """
    Image Analyzer for solar panel defect detection.
    Performs thermal and visual analysis to identify defects.
    """

    def __init__(self):
        """Initialize image analyzer."""
        self.model = None
        logger.info("Image Analyzer initialized")

    def load_model(self):
        """
        Load defect detection model.
        In production, this would load a trained PyTorch/TensorFlow model.
        """
        try:
            model_path = Path(settings.DEFECT_DETECTION_MODEL_PATH)
            if model_path.exists():
                # Load model here
                # self.model = torch.load(model_path)
                logger.info(f"Model loaded from {model_path}")
            else:
                logger.warning(f"Model not found at {model_path}, using mock detection")
        except Exception as e:
            logger.error(f"Error loading model: {e}")

    def decode_image(self, image_base64: str) -> np.ndarray:
        """
        Decode base64 image to numpy array.

        Args:
            image_base64: Base64 encoded image

        Returns:
            Image as numpy array
        """
        try:
            # Remove data URL prefix if present
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]

            # Decode base64
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_bytes))

            # Convert to numpy array
            image_array = np.array(image)

            logger.info(f"Decoded image: {image_array.shape}")
            return image_array

        except Exception as e:
            logger.error(f"Error decoding image: {e}")
            raise ValueError(f"Invalid image data: {e}")

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for analysis.

        Args:
            image: Input image array

        Returns:
            Preprocessed image
        """
        # Resize to standard size
        target_size = (640, 640)
        image_resized = cv2.resize(image, target_size)

        # Convert to RGB if needed
        if len(image_resized.shape) == 2:
            image_resized = cv2.cvtColor(image_resized, cv2.COLOR_GRAY2RGB)
        elif image_resized.shape[2] == 4:
            image_resized = cv2.cvtColor(image_resized, cv2.COLOR_RGBA2RGB)

        return image_resized

    def detect_defects(self, image: np.ndarray) -> List[DetectedDefect]:
        """
        Detect defects in solar panel image.

        Args:
            image: Input image array

        Returns:
            List of detected defects
        """
        logger.info("Performing defect detection...")

        # In production, use trained model
        # For now, use mock detection with image analysis
        defects = self._mock_defect_detection(image)

        logger.info(f"Detected {len(defects)} potential defects")
        return defects

    def _mock_defect_detection(self, image: np.ndarray) -> List[DetectedDefect]:
        """
        Mock defect detection for demonstration.
        In production, replace with actual model inference.

        Args:
            image: Input image

        Returns:
            List of mock defects
        """
        defects = []

        # Convert to grayscale for analysis
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image

        # Simple brightness analysis (mock thermal hotspot detection)
        mean_brightness = np.mean(gray)
        max_brightness = np.max(gray)

        if max_brightness > mean_brightness * 1.3:
            defects.append(DetectedDefect(
                defect_type=DefectType.HOTSPOT,
                confidence=0.75,
                bounding_box=[100, 100, 200, 200],
                severity="medium",
                description="Potential hotspot detected - area showing elevated temperature"
            ))

        # Edge detection for cracks
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size

        if edge_density > 0.1:
            defects.append(DetectedDefect(
                defect_type=DefectType.CRACK,
                confidence=0.65,
                bounding_box=[150, 150, 250, 250],
                severity="high",
                description="Possible micro-crack or cell crack detected"
            ))

        # Variance analysis for discoloration
        variance = np.var(gray)
        if variance < 100:
            defects.append(DetectedDefect(
                defect_type=DefectType.DISCOLORATION,
                confidence=0.55,
                bounding_box=[50, 50, 150, 150],
                severity="low",
                description="Discoloration or UV-induced degradation detected"
            ))

        return defects

    def calculate_health_score(self, defects: List[DetectedDefect]) -> float:
        """
        Calculate overall panel health score.

        Args:
            defects: List of detected defects

        Returns:
            Health score (0-100)
        """
        if not defects:
            return 100.0

        # Base score
        score = 100.0

        # Deduct points based on severity and confidence
        severity_weights = {
            "low": 5,
            "medium": 15,
            "high": 30
        }

        for defect in defects:
            weight = severity_weights.get(defect.severity, 10)
            deduction = weight * defect.confidence
            score -= deduction

        return max(0.0, min(100.0, score))

    def generate_recommendations(self, defects: List[DetectedDefect]) -> List[str]:
        """
        Generate maintenance recommendations based on defects.

        Args:
            defects: List of detected defects

        Returns:
            List of recommendations
        """
        recommendations = []

        if not defects:
            recommendations.append("No defects detected. Panel is in good condition.")
            recommendations.append("Continue regular monitoring and cleaning schedule.")
            return recommendations

        # Group by defect type
        defect_types = set(d.defect_type for d in defects)

        if DefectType.HOTSPOT in defect_types:
            recommendations.append(
                "⚠️ HOTSPOT DETECTED: Immediate inspection recommended. "
                "Check for shading, soiling, or cell mismatch. May indicate bypass diode failure."
            )

        if DefectType.CRACK in defect_types:
            recommendations.append(
                "⚠️ CRACK DETECTED: Schedule detailed inspection. "
                "Micro-cracks can lead to power loss and may worsen over time."
            )

        if DefectType.DISCOLORATION in defect_types:
            recommendations.append(
                "ℹ️ DISCOLORATION: Monitor for progression. "
                "May indicate EVA degradation or UV exposure damage."
            )

        if DefectType.SOILING in defect_types:
            recommendations.append(
                "🧹 SOILING: Clean panels to restore efficiency. "
                "Regular cleaning can improve output by 5-15%."
            )

        # General recommendations
        high_severity = [d for d in defects if d.severity == "high"]
        if high_severity:
            recommendations.append(
                "⚠️ HIGH PRIORITY: Contact certified solar technician for professional assessment."
            )

        return recommendations

    def analyze_image(
        self,
        image_base64: str = None,
        image_path: str = None
    ) -> Tuple[List[DetectedDefect], float, Dict, List[str]]:
        """
        Perform complete image analysis.

        Args:
            image_base64: Base64 encoded image
            image_path: Path to image file

        Returns:
            Tuple of (defects, health_score, dimensions, recommendations)
        """
        # Load image
        if image_base64:
            image = self.decode_image(image_base64)
        elif image_path:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image from {image_path}")
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            raise ValueError("Either image_base64 or image_path must be provided")

        # Get dimensions
        dimensions = {
            "width": image.shape[1],
            "height": image.shape[0]
        }

        # Preprocess
        preprocessed = self.preprocess_image(image)

        # Detect defects
        defects = self.detect_defects(preprocessed)

        # Calculate health score
        health_score = self.calculate_health_score(defects)

        # Generate recommendations
        recommendations = self.generate_recommendations(defects)

        return defects, health_score, dimensions, recommendations


# Global image analyzer instance
image_analyzer = ImageAnalyzer()
