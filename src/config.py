"""
Configuration module for PV Image Analysis System
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
EXAMPLES_DIR = PROJECT_ROOT / "examples"
DEMO_IMAGES_DIR = EXAMPLES_DIR / "demo_images"
TESTS_DIR = PROJECT_ROOT / "tests"
DOCS_DIR = PROJECT_ROOT / "docs"

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CLIP_MODEL = os.getenv("CLIP_MODEL", "ViT-B/32")
GPT4_VISION_MODEL = os.getenv("GPT4_VISION_MODEL", "gpt-4o")

# Image Processing Configuration
MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", "2048"))
SUPPORTED_FORMATS = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"]
DEFECT_CONFIDENCE_THRESHOLD = float(os.getenv("DEFECT_CONFIDENCE_THRESHOLD", "0.6"))

# Model Settings
CLIP_DEVICE = "cuda" if os.getenv("CLIP_DEVICE") == "cuda" else "cpu"
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "8"))

# Report Configuration
REPORT_OUTPUT_DIR = PROJECT_ROOT / "reports"
REPORT_FORMATS = ["pdf", "json", "html"]

# Ensure directories exist
REPORT_OUTPUT_DIR.mkdir(exist_ok=True)
DEMO_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
