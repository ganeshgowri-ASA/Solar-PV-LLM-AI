"""
Setup configuration for Solar PV LLM AI System.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="solar-pv-llm-ai",
    version="0.1.0",
    author="Solar PV AI Team",
    description="Solar PV AI LLM system with incremental training, RAG, citation, and autonomous delivery",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
        ],
        "rag": [
            "chromadb>=0.4.0",
            "sentence-transformers>=2.2.0",
            "langchain>=0.1.0",
        ],
        "llm": [
            "openai>=1.0.0",
            "anthropic>=0.8.0",
        ],
        "docs": [
            "pypdf2>=3.0.0",
            "python-docx>=0.8.11",
            "beautifulsoup4>=4.12.0",
        ]
    },
)
