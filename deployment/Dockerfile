# ============================================
# Multi-Stage Build for Production
# ============================================

# Build stage - for compiling dependencies
FROM python:3.11.7-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip for better dependency resolution
RUN pip install --upgrade pip setuptools wheel

# Copy and install Python dependencies
COPY deployment/requirements.txt .
# Note: torch and transformers are VERY large (1-2GB+) and take 5-15 minutes to download
# This is normal! The build will show progress.
RUN pip install --user --no-cache-dir -r requirements.txt

# ============================================
# Runtime stage - minimal production image
# ============================================
FROM python:3.11.7-slim

# Metadata labels
LABEL maintainer="UNIFY Development Team"
LABEL version="1.0.0"
LABEL description="UNIFY Flask Application - Production Image"

WORKDIR /app

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /root/.local

# Ensure local bin is in PATH for gunicorn
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p src/uploads/notes src/data /app/logs

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV SQLITE_DB_DIR=/app/src/data
ENV SQLITE_DB_NAME=unify_prod.db

# Expose port 5000
EXPOSE 5000

# Health check using Python (no curl dependency)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Run production WSGI server with Gunicorn
# Workers: (2 * CPU cores) + 1 (currently 4 for 2-core systems)
# Timeout: 120s for ML model inference
# Graceful timeout: 30s for clean shutdowns
# Access/error logs to stdout/stderr for Docker logging
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--keep-alive", "5", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "50", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "app:app"]

