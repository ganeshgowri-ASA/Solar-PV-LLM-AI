"""
Image Processor Module

Handles image upload, validation, and preprocessing for PV image analysis.
Supports EL (Electroluminescence), IV curves, and thermal imaging.
"""

import os
import base64
from pathlib import Path
from typing import Union, Tuple, Optional, List
import numpy as np
from PIL import Image
import cv2

import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import MAX_IMAGE_SIZE, SUPPORTED_FORMATS


class ImageProcessor:
    """
    Handles image preprocessing pipeline for PV analysis.

    Supported image types:
    - Electroluminescence (EL) images
    - Thermal/IR images
    - IV curve plots
    - Visual inspection images
    """

    def __init__(self, max_size: int = MAX_IMAGE_SIZE):
        """
        Initialize the image processor.

        Args:
            max_size: Maximum dimension for resizing images
        """
        self.max_size = max_size
        self.supported_formats = SUPPORTED_FORMATS

    def load_image(self, image_path: Union[str, Path]) -> Image.Image:
        """
        Load an image from file path.

        Args:
            image_path: Path to the image file

        Returns:
            PIL Image object

        Raises:
            FileNotFoundError: If image file doesn't exist
            ValueError: If image format is not supported
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        if image_path.suffix.lower() not in self.supported_formats:
            raise ValueError(
                f"Unsupported format: {image_path.suffix}. "
                f"Supported formats: {', '.join(self.supported_formats)}"
            )

        try:
            image = Image.open(image_path)
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return image
        except Exception as e:
            raise ValueError(f"Error loading image: {str(e)}")

    def validate_image(self, image: Image.Image) -> bool:
        """
        Validate image quality and characteristics.

        Args:
            image: PIL Image object

        Returns:
            True if image is valid
        """
        # Check minimum size
        width, height = image.size
        if width < 64 or height < 64:
            raise ValueError(f"Image too small: {width}x{height}. Minimum size is 64x64")

        # Check if image is not completely black or white
        img_array = np.array(image)
        mean_val = np.mean(img_array)
        if mean_val < 5 or mean_val > 250:
            raise ValueError("Image appears to be completely black or white")

        return True

    def resize_image(self, image: Image.Image, max_size: Optional[int] = None) -> Image.Image:
        """
        Resize image while maintaining aspect ratio.

        Args:
            image: PIL Image object
            max_size: Maximum dimension (uses self.max_size if None)

        Returns:
            Resized PIL Image
        """
        max_size = max_size or self.max_size
        width, height = image.size

        if width <= max_size and height <= max_size:
            return image

        # Calculate new dimensions
        if width > height:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            new_height = max_size
            new_width = int(width * (max_size / height))

        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def preprocess_for_clip(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for CLIP model input.

        Args:
            image: PIL Image object

        Returns:
            Preprocessed PIL Image
        """
        # Ensure RGB mode
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Resize to reasonable size for CLIP
        image = self.resize_image(image, max_size=224)

        return image

    def preprocess_for_vision_api(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for GPT-4 Vision API.

        Args:
            image: PIL Image object

        Returns:
            Preprocessed PIL Image
        """
        # Ensure RGB mode
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Resize to optimal size for Vision API
        image = self.resize_image(image, max_size=2048)

        return image

    def enhance_image(self, image: Image.Image, image_type: str = "auto") -> Image.Image:
        """
        Apply enhancement based on image type.

        Args:
            image: PIL Image object
            image_type: Type of PV image ("el", "thermal", "iv", "auto")

        Returns:
            Enhanced PIL Image
        """
        img_array = np.array(image)

        if image_type == "el" or image_type == "auto":
            # Enhance contrast for EL images
            img_array = cv2.convertScaleAbs(img_array, alpha=1.2, beta=10)
        elif image_type == "thermal":
            # Apply colormap for thermal images if grayscale
            if len(img_array.shape) == 2:
                img_array = cv2.applyColorMap(img_array, cv2.COLORMAP_JET)
                img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)

        # Apply adaptive histogram equalization for better visibility
        if len(img_array.shape) == 3:
            # Convert to LAB color space
            lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)

            # Apply CLAHE to L channel
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)

            # Merge and convert back
            lab = cv2.merge([l, a, b])
            img_array = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

        return Image.fromarray(img_array)

    def encode_image_base64(self, image: Image.Image, format: str = "PNG") -> str:
        """
        Encode image to base64 string for API transmission.

        Args:
            image: PIL Image object
            format: Image format for encoding

        Returns:
            Base64 encoded string
        """
        from io import BytesIO

        buffered = BytesIO()
        image.save(buffered, format=format)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str

    def process_image_pipeline(
        self,
        image_path: Union[str, Path],
        image_type: str = "auto",
        enhance: bool = True
    ) -> dict:
        """
        Complete preprocessing pipeline for PV image analysis.

        Args:
            image_path: Path to the image file
            image_type: Type of PV image ("el", "thermal", "iv", "auto")
            enhance: Whether to apply image enhancement

        Returns:
            Dictionary containing processed images and metadata
        """
        # Load image
        original_image = self.load_image(image_path)

        # Validate
        self.validate_image(original_image)

        # Enhance if requested
        if enhance:
            enhanced_image = self.enhance_image(original_image, image_type)
        else:
            enhanced_image = original_image

        # Prepare for different models
        clip_image = self.preprocess_for_clip(enhanced_image)
        vision_image = self.preprocess_for_vision_api(enhanced_image)

        return {
            "original": original_image,
            "enhanced": enhanced_image,
            "clip_ready": clip_image,
            "vision_ready": vision_image,
            "metadata": {
                "original_size": original_image.size,
                "format": Path(image_path).suffix,
                "image_type": image_type,
                "enhanced": enhance
            }
        }

    def batch_process(
        self,
        image_paths: List[Union[str, Path]],
        image_type: str = "auto",
        enhance: bool = True
    ) -> List[dict]:
        """
        Process multiple images in batch.

        Args:
            image_paths: List of image file paths
            image_type: Type of PV images
            enhance: Whether to apply enhancement

        Returns:
            List of processed image dictionaries
        """
        results = []
        for image_path in image_paths:
            try:
                result = self.process_image_pipeline(image_path, image_type, enhance)
                result["path"] = str(image_path)
                result["success"] = True
                results.append(result)
            except Exception as e:
                results.append({
                    "path": str(image_path),
                    "success": False,
                    "error": str(e)
                })

        return results
