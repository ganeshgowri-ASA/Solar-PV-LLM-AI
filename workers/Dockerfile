# =============================================================================
# Dockerfile for Celery Workers
# =============================================================================

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN groupadd -r celeryuser && useradd -r -g celeryuser celeryuser

# Create necessary directories
RUN mkdir -p /app/models /app/cache /app/data /app/logs && \
    chown -R celeryuser:celeryuser /app

# Copy application code
COPY --chown=celeryuser:celeryuser . .

# Switch to non-root user
USER celeryuser

# Default command (can be overridden)
CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info"]
