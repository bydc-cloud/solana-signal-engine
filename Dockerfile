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

# Start both API server and scanner using a startup script
CMD uvicorn api_server:app --host 0.0.0.0 --port ${PORT:-8000} & \
    python REALITY_MOMENTUM_SCANNER.py & \
    wait
