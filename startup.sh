#!/bin/bash

# Define log file location for Azure App Service
LOG_FILE="/home/LogFiles/startup.log"

# Define the working directory where the app files are deployed
APP_DIR="/home/site/wwwroot"

# Log the beginning of the startup sequence
echo "===== STARTING BANK AGENT =====" >> "$LOG_FILE"

# Change to the app directory; exit if it fails
cd "$APP_DIR" || exit 1

# Log and install Python dependencies from requirements.txt
echo "Installing dependencies..." >> "$LOG_FILE"
pip install --no-cache-dir -r requirements.txt >> "$LOG_FILE" 2>&1

# Log and start the FastAPI app using gunicorn + uvicorn worker
echo "Starting gunicorn..." >> "$LOG_FILE"
exec gunicorn app.main:app \
  --workers 1 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 >> "$LOG_FILE" 2>&1
