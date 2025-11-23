"""
Configuration settings for Solar PV LLM AI System
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Application Settings
APP_NAME = os.getenv("APP_NAME", "Solar PV LLM AI System")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))

# File Upload Settings
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "pdf,docx,pptx,png,jpg,jpeg").split(",")

# RAG Settings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# LLM Settings
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4-turbo-preview")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))

# IEC Standards Categories
IEC_STANDARDS = [
    "IEC 61215 - Crystalline Silicon PV Module Testing",
    "IEC 61730 - PV Module Safety Qualification",
    "IEC 61853 - PV Module Performance Testing",
    "IEC 62446 - Grid Connected PV Systems",
    "IEC 60904 - PV Device Measurements",
    "IEC 61724 - PV System Monitoring",
    "IEC 62109 - Power Converters in PV Systems",
    "IEC 61727 - Grid-connected PV Systems",
]

# Test Types
TEST_TYPES = [
    "Performance Testing",
    "Safety Testing",
    "Environmental Testing",
    "Electrical Testing",
    "Mechanical Testing",
    "Thermal Testing",
    "Durability Testing",
    "Certification Testing",
]

# Calculator Types
CALCULATOR_TYPES = [
    "Energy Yield Calculator",
    "System Sizing Calculator",
    "ROI Calculator",
    "Efficiency Calculator",
    "Shading Analysis Calculator",
]

# Page Configuration
PAGE_ICON = "☀️"
LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"
