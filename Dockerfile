# ============================================================
# FLASK FACE RECOGNITION - PRODUCTION DOCKERFILE
# ============================================================
# Base: Python 3.11 slim (lightweight)
# Includes: InsightFace, OpenCV, Flask, PostgreSQL drivers
# ============================================================

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Build tools
    gcc g++ cmake \
    # OpenCV dependencies
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1-mesa-glx \
    # Image processing
    libjpeg-dev \
    libpng-dev \
    # PostgreSQL client
    libpq-dev \
    # Utilities
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p dataset models logs instance data

# Expose ports
EXPOSE 5000
# EXPOSE 443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/halo || exit 1

# Run application
CMD ["python", "run.py"]
