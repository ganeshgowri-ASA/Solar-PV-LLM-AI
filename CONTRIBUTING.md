# Contributing to Solar-PV-LLM-AI

Thank you for your interest in contributing to Solar-PV-LLM-AI! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Documentation](#documentation)

---

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

---

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** (3.11 recommended)
- **Git**
- **Docker & Docker Compose**
- **Node.js 18+** (for frontend development)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR_USERNAME/Solar-PV-LLM-AI.git
cd Solar-PV-LLM-AI
```

3. Add the upstream repository:

```bash
git remote add upstream https://github.com/original-org/Solar-PV-LLM-AI.git
```

---

## Development Environment

### Option 1: Local Development (Recommended for most contributions)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Copy environment file
cp .env.example .env
# Edit .env with your API keys and configuration
```

### Option 2: Docker Development

```bash
# Build and start services
docker-compose up -d

# Run tests in container
docker-compose exec backend pytest tests/
```

### Required Environment Variables

Create a `.env` file with the following minimum configuration:

```bash
# Required for most development
OPENAI_API_KEY=sk-...  # Get from platform.openai.com
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/solar_pv_db
SECRET_KEY=dev-secret-key-change-in-production

# Optional but recommended
ANTHROPIC_API_KEY=sk-ant-...
PINECONE_API_KEY=...
REDIS_URL=redis://localhost:6379/0
```

### Running the Application

```bash
# Start the backend API
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, start Celery worker (if needed)
celery -A backend.services.celery_tasks worker --loglevel=info

# Start the frontend (if working on UI)
cd frontend
streamlit run app.py
```

---

## Code Style Guidelines

### Python Code Style

We follow **PEP 8** with some modifications. Key points:

#### Formatting

- **Line length**: 100 characters maximum
- **Indentation**: 4 spaces (no tabs)
- **Formatter**: Black (automatically applied via pre-commit)

```bash
# Format code manually
black src/ backend/ tests/
```

#### Imports

Use **isort** for import ordering:

```python
# Standard library
import os
import sys
from typing import Dict, List, Optional

# Third-party
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Local
from src.rag_engine import RAGPipeline
from src.utils.exceptions import ValidationError
```

#### Type Hints

Use type hints for all function signatures:

```python
def process_query(
    query: str,
    use_rag: bool = True,
    max_tokens: int = 1000,
) -> Dict[str, Any]:
    """Process a user query and return response with citations."""
    ...
```

#### Docstrings

Use Google-style docstrings:

```python
def calculate_energy_yield(
    capacity_kw: float,
    efficiency: float,
    peak_sun_hours: float,
    system_losses: float = 0.14,
) -> Dict[str, float]:
    """Calculate solar system energy yield.

    Estimates daily, monthly, and annual energy production based on
    system parameters and location-specific solar resource data.

    Args:
        capacity_kw: System capacity in kilowatts.
        efficiency: Panel efficiency as decimal (0-1).
        peak_sun_hours: Average peak sun hours per day.
        system_losses: System losses factor (default: 0.14 for 14%).

    Returns:
        Dictionary containing:
            - daily_kwh: Daily energy production
            - monthly_kwh: Monthly energy production
            - annual_kwh: Annual energy production

    Raises:
        ValueError: If capacity_kw or efficiency is negative.
        ValidationError: If efficiency > 1.

    Example:
        >>> result = calculate_energy_yield(5.0, 0.20, 5.5)
        >>> print(f"Annual: {result['annual_kwh']:.2f} kWh")
        Annual: 8215.60 kWh
    """
    ...
```

### Linting

We use multiple linters:

```bash
# Run all linters
flake8 src/ backend/ tests/
mypy src/ backend/
ruff check src/ backend/

# Or use pre-commit to run all checks
pre-commit run --all-files
```

#### Flake8 Configuration

See `setup.cfg` or `.flake8`:

```ini
[flake8]
max-line-length = 100
extend-ignore = E203, W503
exclude = .git,__pycache__,build,dist,venv
```

#### MyPy Configuration

See `mypy.ini` or `pyproject.toml`:

```ini
[mypy]
python_version = 3.11
strict = true
ignore_missing_imports = true
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Modules | lowercase_with_underscores | `rag_pipeline.py` |
| Classes | PascalCase | `RAGPipeline` |
| Functions | lowercase_with_underscores | `process_query()` |
| Variables | lowercase_with_underscores | `query_result` |
| Constants | UPPERCASE_WITH_UNDERSCORES | `MAX_TOKENS` |
| Private | Leading underscore | `_internal_method()` |

### Error Handling

```python
# Use specific exceptions
from src.utils.exceptions import ValidationError, DocumentNotFoundError

def get_document(doc_id: str) -> Document:
    """Retrieve document by ID.

    Raises:
        DocumentNotFoundError: If document doesn't exist.
        ValidationError: If doc_id format is invalid.
    """
    if not _validate_doc_id(doc_id):
        raise ValidationError(f"Invalid document ID format: {doc_id}")

    document = db.get(doc_id)
    if not document:
        raise DocumentNotFoundError(f"Document not found: {doc_id}")

    return document
```

---

## Testing

### Test Structure

```
tests/
├── unit/                  # Unit tests
│   ├── test_rag_engine.py
│   ├── test_calculators.py
│   └── test_image_analysis.py
├── integration/           # Integration tests
│   ├── test_api_endpoints.py
│   └── test_database.py
├── e2e/                   # End-to-end tests
│   └── test_full_workflow.py
└── conftest.py            # Shared fixtures
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov=backend --cov-report=html

# Run specific test file
pytest tests/unit/test_rag_engine.py

# Run specific test
pytest tests/unit/test_rag_engine.py::test_query_processing

# Run with verbose output
pytest tests/ -v

# Run only fast tests (skip slow/integration)
pytest tests/ -m "not slow"
```

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch

from src.rag_engine.pipeline import RAGPipeline


class TestRAGPipeline:
    """Tests for RAGPipeline class."""

    @pytest.fixture
    def pipeline(self):
        """Create RAGPipeline instance for testing."""
        return RAGPipeline(config={"use_cache": False})

    @pytest.fixture
    def mock_llm_response(self):
        """Mock LLM response for testing."""
        return {
            "response": "Solar panel efficiency...",
            "tokens_used": 150,
        }

    def test_query_returns_response(self, pipeline, mock_llm_response):
        """Test that query returns valid response structure."""
        with patch.object(pipeline, "_call_llm", return_value=mock_llm_response):
            result = pipeline.query("What is solar efficiency?")

        assert "response" in result
        assert "citations" in result
        assert len(result["response"]) > 0

    def test_query_with_empty_input_raises_error(self, pipeline):
        """Test that empty query raises ValidationError."""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            pipeline.query("")

    @pytest.mark.slow
    def test_query_with_real_llm(self, pipeline):
        """Integration test with real LLM (marked as slow)."""
        result = pipeline.query("What is a solar cell?")
        assert result["confidence_score"] > 0.5
```

### Test Coverage Requirements

- **Minimum coverage**: 80% for new code
- **Critical paths**: 100% coverage required for:
  - API endpoints
  - Authentication/authorization
  - Database operations
  - Financial calculations

---

## Pull Request Process

### Before Submitting

1. **Update from upstream**:

```bash
git fetch upstream
git rebase upstream/main
```

2. **Run all checks**:

```bash
# Run pre-commit hooks
pre-commit run --all-files

# Run tests
pytest tests/

# Check types
mypy src/ backend/
```

3. **Update documentation** if needed

### PR Guidelines

#### Branch Naming

```
feature/add-new-calculator
bugfix/fix-citation-extraction
docs/update-api-reference
refactor/improve-rag-pipeline
```

#### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

Examples:

```
feat(rag): add hybrid retrieval with BM25

Implement hybrid search combining BM25 keyword matching
with vector similarity search. Configurable weights via
environment variables.

Closes #123
```

```
fix(api): handle empty query validation

- Add input validation for empty queries
- Return proper 400 error with message
- Add unit tests for edge cases

Fixes #456
```

#### PR Description Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Added unit tests
- [ ] Added integration tests
- [ ] Tested locally
- [ ] All tests pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Added/updated documentation
- [ ] No new warnings

## Related Issues
Closes #XXX
```

### Review Process

1. All PRs require at least one approval
2. CI checks must pass
3. No merge conflicts
4. Documentation updated if applicable

---

## Issue Guidelines

### Bug Reports

Include:

- **Environment**: OS, Python version, relevant package versions
- **Steps to reproduce**: Clear, numbered steps
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Logs/errors**: Relevant error messages or stack traces
- **Screenshots**: If applicable

Template:

```markdown
**Environment**
- OS: Ubuntu 22.04
- Python: 3.11.5
- Package versions: (run `pip freeze | grep -E "fastapi|pydantic|openai"`)

**Steps to Reproduce**
1. Start the API server
2. Send POST request to /api/v1/query/ with body {...}
3. Observe error

**Expected Behavior**
Should return a response with citations.

**Actual Behavior**
Returns 500 Internal Server Error.

**Error Logs**
```
Traceback (most recent call last):
  ...
```

**Additional Context**
Any other relevant information.
```

### Feature Requests

Include:

- **Problem statement**: What problem does this solve?
- **Proposed solution**: How should it work?
- **Alternatives considered**: Other approaches you've thought about
- **Additional context**: Any other relevant information

---

## Documentation

### When to Update Documentation

- Adding new features
- Changing API endpoints
- Modifying configuration options
- Adding new dependencies
- Changing deployment procedures

### Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Project overview, quick start |
| `ARCHITECTURE.md` | System design, components |
| `DEPLOYMENT.md` | Deployment instructions |
| `API_REFERENCE.md` | API documentation |
| `CONTRIBUTING.md` | Contribution guidelines |

### Docstring Requirements

All public modules, classes, and functions must have docstrings:

```python
"""Module docstring describing the module's purpose.

This module provides functionality for X, Y, and Z.
It is used by the RAG pipeline for document retrieval.

Example:
    >>> from src.module import function
    >>> result = function(arg)
"""


class MyClass:
    """Class docstring describing the class.

    Attributes:
        attr1: Description of attr1.
        attr2: Description of attr2.
    """

    def method(self, arg: str) -> bool:
        """Method docstring.

        Args:
            arg: Description of argument.

        Returns:
            Description of return value.

        Raises:
            ValueError: When arg is invalid.
        """
```

---

## Development Workflow

### Feature Development

```bash
# 1. Create feature branch
git checkout -b feature/my-new-feature

# 2. Make changes, commit frequently
git add .
git commit -m "feat(scope): add initial implementation"

# 3. Push to your fork
git push origin feature/my-new-feature

# 4. Open PR on GitHub

# 5. Address review feedback
git commit -m "fix: address review comments"
git push origin feature/my-new-feature
```

### Staying Up to Date

```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main
git push origin main

# Rebase feature branch
git checkout feature/my-feature
git rebase main
```

---

## Questions?

- Open a [Discussion](https://github.com/your-org/Solar-PV-LLM-AI/discussions)
- Join our [Discord/Slack]
- Email: contributors@your-domain.com

Thank you for contributing!
