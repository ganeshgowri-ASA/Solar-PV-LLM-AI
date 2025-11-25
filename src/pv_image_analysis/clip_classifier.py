"""
CLIP Defect Classifier Module

Uses OpenAI's CLIP model for zero-shot classification of PV panel defects.
"""

import torch
import clip
from PIL import Image
from typing import List, Dict, Tuple, Optional
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config import CLIP_MODEL, CLIP_DEVICE, DEFECT_CONFIDENCE_THRESHOLD


class CLIPDefectClassifier:
    """
    CLIP-based classifier for PV panel defect detection and classification.

    Uses zero-shot learning to classify various types of defects in
    photovoltaic panels from EL, thermal, and visual inspection images.
    """

    # Defect categories based on common PV defects
    DEFECT_CATEGORIES = {
        "cell_crack": "a solar panel cell with visible cracks or fractures",
        "hotspot": "a solar panel with hot spots or thermal anomalies",
        "delamination": "a solar panel with delamination or layer separation",
        "discoloration": "a solar panel with discoloration or browning",
        "snail_trail": "a solar panel with snail trail defects",
        "pid": "a solar panel with potential induced degradation",
        "burn_mark": "a solar panel with burn marks or scorching",
        "broken_cell": "a solar panel with broken or shattered cells",
        "micro_crack": "a solar panel with micro-cracks visible in EL imaging",
        "inactive_cell": "a solar panel with inactive or dead cells",
        "finger_interruption": "a solar panel with finger interruption defects",
        "busbar_corrosion": "a solar panel with busbar corrosion or degradation",
        "soldering_defect": "a solar panel with soldering defects",
        "junction_box_issue": "a solar panel with junction box problems",
        "no_defect": "a normal, healthy solar panel without defects"
    }

    def __init__(
        self,
        model_name: str = CLIP_MODEL,
        device: Optional[str] = None,
        confidence_threshold: float = DEFECT_CONFIDENCE_THRESHOLD
    ):
        """
        Initialize the CLIP classifier.

        Args:
            model_name: CLIP model variant (e.g., "ViT-B/32", "ViT-L/14")
            device: Device to use ("cuda" or "cpu"), auto-detected if None
            confidence_threshold: Minimum confidence for defect detection
        """
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold

        # Determine device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        # Load CLIP model
        self._load_model()

        # Prepare text prompts
        self._prepare_text_features()

    def _load_model(self):
        """Load CLIP model and preprocessing."""
        try:
            self.model, self.preprocess = clip.load(self.model_name, device=self.device)
            self.model.eval()
            print(f"CLIP model '{self.model_name}' loaded on {self.device}")
        except Exception as e:
            raise RuntimeError(f"Failed to load CLIP model: {str(e)}")

    def _prepare_text_features(self):
        """Precompute text features for defect categories."""
        self.category_names = list(self.DEFECT_CATEGORIES.keys())
        self.category_prompts = [self.DEFECT_CATEGORIES[cat] for cat in self.category_names]

        # Tokenize text
        text_tokens = clip.tokenize(self.category_prompts).to(self.device)

        # Compute text features
        with torch.no_grad():
            self.text_features = self.model.encode_text(text_tokens)
            self.text_features /= self.text_features.norm(dim=-1, keepdim=True)

    def classify_image(self, image: Image.Image, top_k: int = 5) -> List[Dict[str, any]]:
        """
        Classify a single PV image for defects.

        Args:
            image: PIL Image object
            top_k: Number of top predictions to return

        Returns:
            List of predictions with category, description, and confidence
        """
        # Preprocess image
        image_input = self.preprocess(image).unsqueeze(0).to(self.device)

        # Compute image features
        with torch.no_grad():
            image_features = self.model.encode_image(image_input)
            image_features /= image_features.norm(dim=-1, keepdim=True)

            # Compute similarity scores
            similarity = (100.0 * image_features @ self.text_features.T).softmax(dim=-1)
            scores = similarity[0].cpu().numpy()

        # Get top-k predictions
        top_indices = np.argsort(scores)[-top_k:][::-1]

        predictions = []
        for idx in top_indices:
            category = self.category_names[idx]
            confidence = float(scores[idx])

            predictions.append({
                "category": category,
                "description": self.DEFECT_CATEGORIES[category],
                "confidence": confidence,
                "is_defect": category != "no_defect" and confidence >= self.confidence_threshold
            })

        return predictions

    def classify_batch(
        self,
        images: List[Image.Image],
        top_k: int = 5
    ) -> List[List[Dict[str, any]]]:
        """
        Classify multiple images in batch.

        Args:
            images: List of PIL Image objects
            top_k: Number of top predictions per image

        Returns:
            List of prediction lists
        """
        results = []
        for image in images:
            predictions = self.classify_image(image, top_k)
            results.append(predictions)

        return results

    def detect_defects(
        self,
        image: Image.Image,
        threshold: Optional[float] = None
    ) -> Dict[str, any]:
        """
        Detect if image contains defects above confidence threshold.

        Args:
            image: PIL Image object
            threshold: Confidence threshold (uses default if None)

        Returns:
            Dictionary with defect detection results
        """
        threshold = threshold or self.confidence_threshold
        predictions = self.classify_image(image, top_k=len(self.category_names))

        # Filter defects above threshold
        detected_defects = [
            pred for pred in predictions
            if pred["is_defect"] and pred["confidence"] >= threshold
        ]

        # Get top prediction
        top_prediction = predictions[0]

        # Determine if panel has defects
        has_defects = (
            top_prediction["category"] != "no_defect" and
            top_prediction["confidence"] >= threshold
        )

        return {
            "has_defects": has_defects,
            "top_prediction": top_prediction,
            "detected_defects": detected_defects,
            "all_predictions": predictions,
            "confidence_threshold": threshold
        }

    def add_custom_categories(self, custom_categories: Dict[str, str]):
        """
        Add custom defect categories to the classifier.

        Args:
            custom_categories: Dictionary mapping category names to descriptions
        """
        # Add to existing categories
        self.DEFECT_CATEGORIES.update(custom_categories)

        # Recompute text features
        self._prepare_text_features()

    def get_defect_summary(self, predictions: List[Dict[str, any]]) -> str:
        """
        Generate human-readable summary of defect predictions.

        Args:
            predictions: List of prediction dictionaries

        Returns:
            Formatted summary string
        """
        if not predictions:
            return "No predictions available"

        top_pred = predictions[0]

        if top_pred["category"] == "no_defect":
            return f"No defects detected (confidence: {top_pred['confidence']:.2%})"

        defects = [p for p in predictions if p["is_defect"]]

        if not defects:
            return "No significant defects detected"

        summary = f"Detected {len(defects)} potential defect(s):\n"
        for i, defect in enumerate(defects[:3], 1):
            category = defect["category"].replace("_", " ").title()
            confidence = defect["confidence"]
            summary += f"{i}. {category} (confidence: {confidence:.2%})\n"

        return summary.strip()

    def compare_images(
        self,
        image1: Image.Image,
        image2: Image.Image
    ) -> Dict[str, any]:
        """
        Compare two PV images to detect differences in defects.

        Args:
            image1: First PIL Image
            image2: Second PIL Image

        Returns:
            Comparison results
        """
        results1 = self.detect_defects(image1)
        results2 = self.detect_defects(image2)

        return {
            "image1": results1,
            "image2": results2,
            "difference": {
                "defect_change": results2["has_defects"] != results1["has_defects"],
                "top_category_change": (
                    results1["top_prediction"]["category"] !=
                    results2["top_prediction"]["category"]
                )
            }
        }
