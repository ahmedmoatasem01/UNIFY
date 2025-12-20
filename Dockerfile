# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    unixodbc-dev \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip for better dependency resolution
RUN pip install --upgrade pip setuptools wheel

# Copy requirements file first (for better Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
# Note: torch and transformers are VERY large (1-2GB+) and take 5-15 minutes to download
# This is normal! The build will show progress.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create necessary directories
RUN mkdir -p src/uploads/notes src/data

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV SQLITE_DB_DIR=/app/src/data
ENV SQLITE_DB_NAME=unify_dev.db

# Expose port 5000
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]

