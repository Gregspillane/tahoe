# Use Python 3.11 as base image (meets 3.9+ requirement)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Set Python path
ENV PYTHONPATH=/app:$PYTHONPATH

# Expose port for Tahoe API
EXPOSE 9000

# Default command to run Tahoe API server
CMD ["uvicorn", "src.tahoe.api.main:app", "--host", "0.0.0.0", "--port", "9000"]