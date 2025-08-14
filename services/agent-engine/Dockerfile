# Multi-stage build for smaller final image
FROM python:3.12-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH=/home/appuser/.local/bin:$PATH \
    ENVIRONMENT=production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy Python packages from builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser config/ ./config/
COPY --chown=appuser:appuser scripts/ ./scripts/
COPY --chown=appuser:appuser examples/ ./examples/
COPY --chown=appuser:appuser specs/ ./specs/

# Copy Prisma schema 
COPY --chown=appuser:appuser prisma/ ./prisma/

# Generate Prisma client during build
# Set up environment and generate client in the correct location
ENV PATH="/home/appuser/.local/bin:$PATH"
ENV PYTHONPATH="/home/appuser/.local/lib/python3.12/site-packages"
RUN cd prisma && \
    python -m pip install --user prisma && \
    python -c "import prisma; print('Prisma installed')" && \
    prisma generate && \
    chown -R appuser:appuser /home/appuser/.local

# Create runtime directories that need write access (do this before switching users)
RUN mkdir -p versions && chown -R appuser:appuser versions

# Note: .env file will be mounted in development
# In production, environment variables come from Helm/Vault

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]