"""
Utility functions for PV image analysis.
"""

import numpy as np
from PIL import Image
from typing import Dict, List, Tuple, Optional
import cv2


def calculate_image_quality(image: Image.Image) -> Dict[str, float]:
    """
    Calculate quality metrics for an image.

    Args:
        image: PIL Image object

    Returns:
        Dictionary with quality metrics
    """
    img_array = np.array(image)

    # Convert to grayscale for analysis
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array

    # Calculate metrics
    metrics = {
        "mean_brightness": float(np.mean(gray)),
        "std_brightness": float(np.std(gray)),
        "contrast": float(gray.max() - gray.min()),
        "sharpness": float(cv2.Laplacian(gray, cv2.CV_64F).var())
    }

    return metrics


def detect_image_type(image: Image.Image) -> str:
    """
    Automatically detect the type of PV image.

    Args:
        image: PIL Image object

    Returns:
        Detected image type ("el", "thermal", "iv", "visual")
    """
    img_array = np.array(image)

    # Check if grayscale (likely EL or thermal)
    if len(img_array.shape) == 2 or (len(img_array.shape) == 3 and
                                      np.allclose(img_array[:, :, 0], img_array[:, :, 1])):

        # EL images typically have dark background with bright cells
        mean_val = np.mean(img_array)

        if mean_val < 80:  # Dark background suggests EL
            return "el"
        else:
            return "thermal"

    # Check for IV curve characteristics (plot-like appearance)
    if img_array.shape[0] < img_array.shape[1]:  # Wider than tall suggests plot
        # Check for grid patterns typical of plots
        edges = cv2.Canny(cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY), 50, 150)
        if np.sum(edges) / edges.size > 0.05:  # Significant edge density
            return "iv"

    return "visual"


def compare_images(image1: Image.Image, image2: Image.Image) -> Dict:
    """
    Compare two images and calculate similarity metrics.

    Args:
        image1: First PIL Image
        image2: Second PIL Image

    Returns:
        Dictionary with comparison metrics
    """
    # Resize to same size if different
    if image1.size != image2.size:
        size = (min(image1.width, image2.width), min(image1.height, image2.height))
        image1 = image1.resize(size)
        image2 = image2.resize(size)

    img1_array = np.array(image1)
    img2_array = np.array(image2)

    # Calculate metrics
    mse = float(np.mean((img1_array - img2_array) ** 2))
    mae = float(np.mean(np.abs(img1_array - img2_array)))

    # Normalized cross-correlation
    correlation = float(np.corrcoef(img1_array.flatten(), img2_array.flatten())[0, 1])

    return {
        "mean_squared_error": mse,
        "mean_absolute_error": mae,
        "correlation": correlation,
        "similarity_score": 1.0 / (1.0 + mse / 10000)  # Normalized similarity
    }


def extract_cells_from_el_image(image: Image.Image) -> List[Image.Image]:
    """
    Attempt to segment individual cells from an EL image.

    Args:
        image: PIL Image of EL panel

    Returns:
        List of cell images
    """
    img_array = np.array(image)

    # Convert to grayscale
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array

    # Apply threshold
    _, binary = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours by area and aspect ratio
    cells = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 500:  # Minimum area threshold
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h

            # Solar cells are typically square
            if 0.8 < aspect_ratio < 1.2:
                cell_img = image.crop((x, y, x + w, y + h))
                cells.append(cell_img)

    return cells


def create_defect_heatmap(
    image: Image.Image,
    defect_locations: List[Dict]
) -> np.ndarray:
    """
    Create a heatmap overlay showing defect locations.

    Args:
        image: Original PIL Image
        defect_locations: List of defect dictionaries with location info

    Returns:
        Numpy array with heatmap overlay
    """
    img_array = np.array(image)
    heatmap = np.zeros(img_array.shape[:2], dtype=np.float32)

    # Add gaussian blobs for each defect location
    for defect in defect_locations:
        # This is simplified - would need actual coordinates
        # For demonstration, create random hotspots
        severity_weight = {
            "Low": 0.25,
            "Medium": 0.5,
            "High": 0.75,
            "Critical": 1.0
        }.get(defect.get("severity", "Medium"), 0.5)

        # In real implementation, would use actual coordinates
        # Here we just show the concept
        heatmap += severity_weight

    # Normalize
    if heatmap.max() > 0:
        heatmap = heatmap / heatmap.max()

    # Apply colormap
    heatmap_colored = cv2.applyColorMap(
        (heatmap * 255).astype(np.uint8),
        cv2.COLORMAP_JET
    )

    # Blend with original
    overlay = cv2.addWeighted(
        img_array,
        0.7,
        cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB),
        0.3,
        0
    )

    return overlay


def estimate_power_loss(defect_type: str, defect_count: int) -> Dict[str, float]:
    """
    Estimate power loss based on defect type and count.

    Args:
        defect_type: Type of defect
        defect_count: Number of defects

    Returns:
        Dictionary with power loss estimates
    """
    # Typical power loss percentages per defect
    loss_per_defect = {
        "cell_crack": 5.0,
        "micro_crack": 2.0,
        "dead_cell": 3.0,  # Per cell in series string
        "hotspot": 10.0,
        "pid": 15.0,
        "finger_interruption": 3.0,
        "busbar_interruption": 50.0,
        "delamination": 8.0,
        "shunt": 12.0
    }

    base_loss = loss_per_defect.get(defect_type.lower().replace(" ", "_"), 5.0)

    # Calculate total loss (not simply additive due to complex interactions)
    if defect_count == 1:
        total_loss = base_loss
    else:
        # Diminishing returns on additional defects
        total_loss = base_loss * (1 + 0.7 * (defect_count - 1))

    return {
        "base_loss_per_defect": base_loss,
        "total_estimated_loss": min(total_loss, 100.0),  # Cap at 100%
        "defect_count": defect_count,
        "confidence": "low"  # Estimation confidence
    }


def validate_api_key(api_key: str) -> bool:
    """
    Validate OpenAI API key format.

    Args:
        api_key: API key string

    Returns:
        True if format appears valid
    """
    if not api_key:
        return False

    # OpenAI keys start with 'sk-'
    if not api_key.startswith('sk-'):
        return False

    # Check minimum length
    if len(api_key) < 20:
        return False

    return True


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "2.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0

    return f"{size_bytes:.1f} TB"


def get_image_info(image_path: str) -> Dict:
    """
    Get detailed information about an image file.

    Args:
        image_path: Path to image file

    Returns:
        Dictionary with image information
    """
    from pathlib import Path

    path = Path(image_path)

    if not path.exists():
        return {"error": "File not found"}

    image = Image.open(path)
    file_size = path.stat().st_size

    return {
        "filename": path.name,
        "format": image.format,
        "mode": image.mode,
        "size": image.size,
        "width": image.width,
        "height": image.height,
        "file_size": format_file_size(file_size),
        "file_size_bytes": file_size,
        "path": str(path.absolute())
    }
