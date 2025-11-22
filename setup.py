"""
Setup script for IEC PDF Ingestion Pipeline.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="iec-pdf-ingestion",
    version="0.1.0",
    description="IEC PDF ingestion pipeline with intelligent chunking and Q&A generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Solar PV LLM AI Team",
    author_email="",
    url="https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "PyPDF2>=3.0.1",
        "pdfplumber>=0.10.3",
        "pypdf>=3.17.4",
        "langchain>=0.1.0",
        "langchain-community>=0.0.10",
        "tiktoken>=0.5.2",
        "sentence-transformers>=2.2.2",
        "spacy>=3.7.2",
        "openai>=1.6.1",
        "pandas>=2.1.4",
        "numpy>=1.26.2",
        "click>=8.1.7",
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.3",
        "pyyaml>=6.0.1",
        "tqdm>=4.66.1",
        "colorlog>=6.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "ingest-iec-pdf=ingest_iec_pdf:cli",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="iec pdf ingestion chunking qa-generation rag llm solar-pv",
    project_urls={
        "Documentation": "https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI/blob/main/PIPELINE_DOCUMENTATION.md",
        "Source": "https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI",
        "Tracker": "https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI/issues",
    },
)
