# Use Python 3.12 (same as your old working setup)
FROM python:3.12-slim

# Environment setup
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies (keep since your old setup had them)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Ensure startup script is executable
RUN chmod +x startup.sh

# Expose port
EXPOSE 8000

# Run startup script
CMD ["./startup.sh"]