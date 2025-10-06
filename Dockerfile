# Dockerfile for Helix Trading Bot - Railway Deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p data

# Expose port (Railway sets $PORT env var)
EXPOSE ${PORT:-8000}

# Start AURA unified server and scanner
CMD python3 init_db.py && \
    python3 init_aura_db.py && \
    uvicorn aura_server:app --host 0.0.0.0 --port ${PORT:-8000} & \
    python3 REALITY_MOMENTUM_SCANNER.py & \
    wait
