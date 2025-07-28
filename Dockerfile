# Use a minimal Python 3.12 image
FROM python:3.12-slim

# Environment setup
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system-level dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy all app code
COPY . .

# Make sure startup script is executable
RUN chmod +x startup.sh

# Expose port
EXPOSE 8000

# Run startup script
CMD ["./startup.sh"]
