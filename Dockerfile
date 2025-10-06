# Dockerfile for AURA v0.3.0 - Railway Deployment
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

# Make start script executable
RUN chmod +x start.sh

# Expose port (Railway sets $PORT env var)
EXPOSE ${PORT:-8000}

# Start AURA using startup script with better error handling
CMD ["./start.sh"]
